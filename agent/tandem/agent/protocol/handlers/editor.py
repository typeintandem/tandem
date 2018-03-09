import json
import os
import logging
import socket
import uuid
import tandem.agent.protocol.messages.editor as em
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    NewOperations,
    Hello
)
from tandem.agent.stores.connection import ConnectionStore
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    ConnectRequest,
)
from tandem.agent.configuration import RENDEZVOUS_ADDRESS


class EditorProtocolHandler:
    def __init__(self, id, std_streams, gateway, document):
        self._id = id
        self._std_streams = std_streams
        self._gateway = gateway
        self._document = document

    def handle_message(self, retrieve_io_data):
        io_data = retrieve_io_data()
        data = io_data.get_data()

        try:
            message = em.deserialize(data)
            if type(message) is em.ConnectTo:
                self._handle_connect_to(message)
            elif type(message) is em.WriteRequestAck:
                self._handle_write_request_ack(message)
            elif type(message) is em.NewPatches:
                self._handle_new_patches(message)
            elif type(message) is em.CheckDocumentSync:
                self._handle_check_document_sync(message)
            elif type(message) is em.HostSession:
                self._handle_host_session(message)
            elif type(message) is em.JoinSession:
                self._handle_join_session(message)
        except em.EditorProtocolMarshalError:
            logging.info("Ignoring invalid editor protocol message.")
        except:
            logging.exception(
                "Exception when handling editor protocol message:")
            raise

    def _handle_connect_to(self, message):
        hostname = socket.gethostbyname(message.host)
        logging.info(
            "Tandem Agent is attempting to establish a direct"
            " connection to {}:{}.".format(hostname, message.port),
        )

        address = (hostname, message.port)
        payload = InteragentProtocolUtils.serialize(Hello(
            id=str(self._id),
            should_reply=True,
        ))
        io_data = self._gateway.generate_io_data(payload, address)
        self._gateway.write_io_data(io_data)

    def _handle_write_request_ack(self, message):
        logging.debug("Received ACK for seq: {}".format(message.seq))
        text_patches = self._document.apply_queued_operations()
        self._document.set_write_request_sent(False)
        # Even if no text patches need to be applied, we need to reply to
        # the plugin to allow it to accept changes from the user again
        text_patches_message = em.ApplyPatches(text_patches)
        io_data = self._std_streams.generate_io_data(
            em.serialize(text_patches_message),
        )
        self._std_streams.write_io_data(io_data)
        logging.debug(
            "Sent apply patches message for seq: {}".format(message.seq),
        )

    def _handle_new_patches(self, message):
        nested_operations = [
            self._document.set_text_in_range(
                patch["start"],
                patch["end"],
                patch["text"],
            )
            for patch in message.patch_list
        ]
        operations = []
        for operations_list in nested_operations:
            operations.extend(operations_list)

        connections = ConnectionStore.get_instance().get_open_connections()
        if len(connections) == 0:
            return

        addresses = [
            connection.get_active_address() for connection in connections
        ]
        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_list=json.dumps(operations)
        ))
        io_data = self._gateway.generate_io_data(payload, addresses)
        self._gateway.write_io_data(
            io_data,
            reliability=True,
        )

    def _handle_check_document_sync(self, message):
        document_text_content = self._document.get_document_text()

        # TODO: ignore all other messages until we receive an ack
        contents = os.linesep.join(message.contents) + os.linesep

        if (contents != document_text_content):
            document_lines = document_text_content.split(os.linesep)
            apply_text = em.serialize(em.ApplyText(document_lines))
            io_data = self._std_streams.generate_io_data(apply_text)
            self._std_streams.write_io_data(io_data)

    def _handle_host_session(self, message):
        # Register with rendezvous
        session_id = uuid.uuid4()
        self._send_connect_request(session_id)

        # Inform plugin of session id
        session_info = em.serialize(em.SessionInfo(session_id=str(session_id)))
        io_data = self._std_streams.generate_io_data(session_info)
        self._std_streams.write_io_data(io_data)

    def _handle_join_session(self, message):
        # Parse ID to make sure it's a UUID
        session_id = uuid.UUID(message.session_id)
        self._send_connect_request(session_id)

    def _send_connect_request(self, session_id):
        io_data = self._gateway.generate_io_data(
            RendezvousProtocolUtils.serialize(ConnectRequest(
                session_id=str(session_id),
                my_id=str(self._id),
                private_address=(
                    socket.gethostbyname(socket.gethostname()),
                    self._gateway.get_port(),
                ),
            )),
            RENDEZVOUS_ADDRESS,
        )
        self._gateway.write_io_data(io_data)

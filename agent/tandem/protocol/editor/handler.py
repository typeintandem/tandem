import json
import os
import logging
import socket
import tandem.protocol.editor.messages as em

from tandem.models.peer import Peer
from tandem.stores.peer import PeerStore
from tandem.protocol.interagent.messages import (
    InteragentProtocolUtils,
    NewOperations,
    Hello
)


class EditorProtocolHandler:
    def __init__(self, std_streams, gateway, document):
        self._std_streams = std_streams
        self._gateway = gateway
        self._document = document

    def handle_message(self, data):
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
        except em.EditorProtocolMarshalError:
            logging.info("Ignoring invalid editor protocol message.")
        except:
            logging.exception(
                "Exception when handling editor protocol message:")
            raise

    def _handle_connect_to(self, message):
        hostname = socket.gethostbyname(message.host)
        logging.info(
            "Tandem Agent is attempting to establish a "
            "connection to {}:{}.".format(hostname, message.port),
        )

        address = (hostname, message.port)
        new_peer = Peer(address)
        payload = InteragentProtocolUtils.serialize(Hello())
        self._gateway.write_data(payload, address)
        PeerStore.get_instance().add_peer(new_peer)

        logging.info(
            "Tandem Agent connected to {}:{}."
            .format(hostname, message.port),
        )

    def _handle_write_request_ack(self, message):
        logging.debug("Received ACK for seq: {}".format(message.seq))
        text_patches = self._document.apply_queued_operations()
        self._document.set_write_request_sent(False)
        # Even if no text patches need to be applied, we need to reply to
        # the plugin to allow it to accept changes from the user again
        text_patches_message = em.ApplyPatches(text_patches)
        self._std_streams.write_string_message(
            em.serialize(text_patches_message),
        )
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

        peers = PeerStore.get_instance().get_peers()
        addresses = [peer.get_address() for peer in peers]
        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_binary=json.dumps(operations)
        ))
        self._gateway.write_data(payload, addresses)

    def _handle_check_document_sync(self, message):
        document_text_content = self._document.get_document_text()

        # TODO: ignore all other messages until we receive an ack
        contents = os.linesep.join(message.contents) + os.linesep

        if (contents != document_text_content):
            document_lines = document_text_content.split(os.linesep)
            apply_text = em.serialize(em.ApplyText(document_lines))
            self._std_streams.write_string_message(apply_text)

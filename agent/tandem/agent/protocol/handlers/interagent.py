import logging
import json
import uuid
import tandem.agent.protocol.messages.editor as em

from tandem.agent.models.connection import DirectConnection
from tandem.agent.models.connection_state import ConnectionState
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolMessageType,
    InteragentProtocolUtils,
    NewOperations,
    Bye,
    Hello,
    PingBack,
)
from tandem.agent.stores.connection import ConnectionStore
from tandem.agent.utils.hole_punching import HolePunchingUtils
from tandem.shared.models.peer import Peer
from tandem.shared.protocol.handlers.addressed import AddressedHandler
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolHandler(AddressedHandler):
    @staticvalue
    def _protocol_message_utils(self):
        return InteragentProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            InteragentProtocolMessageType.Ping.value: self._handle_ping,
            InteragentProtocolMessageType.PingBack.value:
                self._handle_pingback,
            InteragentProtocolMessageType.Syn.value: self._handle_syn,
            InteragentProtocolMessageType.Hello.value: self._handle_hello,
            InteragentProtocolMessageType.Bye.value: self._handle_bye,
            InteragentProtocolMessageType.NewOperations.value:
                self._handle_new_operations,
        }

    def __init__(self, id, std_streams, gateway, document, time_scheduler):
        self._id = id
        self._std_streams = std_streams
        self._gateway = gateway
        self._document = document
        self._time_scheduler = time_scheduler
        self._next_editor_sequence = 0

    def _handle_ping(self, message, sender_address):
        peer_id = uuid.UUID(message.id)
        connection = \
            ConnectionStore.get_instance().get_connection_by_id(peer_id)

        # Only reply to peers we know about to prevent the other peer from
        # thinking it can reach us successfully
        if connection is None:
            return

        logging.debug(
            "Replying to ping from {} at {}:{}."
            .format(message.id, *sender_address),
        )
        io_data = self._gateway.generate_io_data(
            InteragentProtocolUtils.serialize(PingBack(id=str(self._id))),
            sender_address,
        )
        self._gateway.write_io_data(io_data)

    def _handle_pingback(self, message, sender_address):
        peer_id = uuid.UUID(message.id)
        connection = \
            ConnectionStore.get_instance().get_connection_by_id(peer_id)
        # Only count PingBack messages from peers we know about and from whom
        # we expect PingBack messages
        if (connection is None or
                connection.get_connection_state() != ConnectionState.PING):
            return

        logging.debug(
            "Counting ping from {} at {}:{}."
            .format(message.id, *sender_address),
        )
        connection.bump_ping_count(sender_address)

        # When the connection is ready to transition into the SYN/WAIT states,
        # an active address will be available
        if connection.get_active_address() is None:
            return

        connection.set_connection_state(
            ConnectionState.SEND_SYN
            if connection.initiated_connection()
            else ConnectionState.WAIT_FOR_SYN
        )
        logging.debug(
            "Promoted peer from {} with address {}:{}."
            .format(message.id, *(connection.get_active_address())),
        )

        if connection.get_connection_state() == ConnectionState.SEND_SYN:
            logging.debug(
                "Will send SYN to {} at {}:{}"
                .format(message.id, *(connection.get_active_address())),
            )
            connection.set_interval_handle(self._time_scheduler.run_every(
                HolePunchingUtils.SYN_INTERVAL,
                HolePunchingUtils.generate_send_syn(
                    self._gateway,
                    connection.get_active_address(),
                ),
            ))
        else:
            logging.debug(
                "Will wait for SYN from {} at {}:{}"
                .format(message.id, *(connection.get_active_address())),
            )

    def _handle_syn(self, message, sender_address):
        logging.debug("Received SYN from {}:{}".format(*sender_address))
        connection = (
            ConnectionStore.get_instance()
            .get_connection_by_address(sender_address)
        )
        if (connection is None or
                connection.get_connection_state() == ConnectionState.SEND_SYN):
            return

        connection.set_connection_state(ConnectionState.OPEN)
        self._send_all_operations(connection, even_if_empty=True)
        logging.debug(
            "Connection to peer at {}:{} is open."
            .format(*(connection.get_active_address())),
        )

    def _handle_hello(self, message, sender_address):
        id = uuid.UUID(message.id)
        new_connection = DirectConnection(Peer(
            id=id,
            public_address=sender_address,
        ))
        ConnectionStore.get_instance().add_connection(new_connection)
        logging.info(
            "Tandem Agent established a direct connection to {}:{}"
            .format(*sender_address),
        )

        if message.should_reply:
            io_data = self._gateway.generate_io_data(
                InteragentProtocolUtils.serialize(Hello(
                    id=str(self._id),
                    should_reply=False,
                )),
                sender_address,
            )
            self._gateway.write_io_data(io_data)

        self._send_all_operations(new_connection)

    def _handle_bye(self, message, sender_address):
        connection_store = ConnectionStore.get_instance()
        connection = connection_store.get_connection_by_address(sender_address)
        if connection is None:
            return
        connection_store.remove_connection(connection)

    def _handle_new_operations(self, message, sender_address):
        connection = (
            ConnectionStore.get_instance()
            .get_connection_by_address(sender_address)
        )
        if (connection is not None and
                connection.get_connection_state() == ConnectionState.SEND_SYN):
            connection.set_connection_state(ConnectionState.OPEN)
            logging.debug(
                "Connection to peer at {}:{} is open."
                .format(*(connection.get_active_address())),
            )

        operations_list = json.loads(message.operations_list)
        if len(operations_list) == 0:
            return
        self._document.enqueue_remote_operations(operations_list)

        if not self._document.write_request_sent():
            io_data = self._std_streams.generate_io_data(
                em.serialize(em.WriteRequest(self._next_editor_sequence)),
            )
            self._std_streams.write_io_data(io_data)
            self._document.set_write_request_sent(True)
            logging.debug(
                "Sent write request seq: {}"
                .format(self._next_editor_sequence),
            )
            self._next_editor_sequence += 1

    def _send_all_operations(self, connection, even_if_empty=False):
        operations = self._document.get_document_operations()
        if not even_if_empty and len(operations) == 0:
            return

        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_list=json.dumps(operations)
        ))
        io_data = self._gateway.generate_io_data(
            payload,
            connection.get_active_address(),
        )
        self._gateway.write_io_data(
            io_data,
            reliability=True,
        )

    def stop(self):
        connections = ConnectionStore.get_instance().get_open_connections()
        io_data = self._gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Bye()),
            [connection.get_active_address() for connection in connections],
        )
        self._gateway.write_io_data(io_data)
        ConnectionStore.reset_instance()

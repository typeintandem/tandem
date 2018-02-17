import logging
import json
import tandem.agent.protocol.messages.editor as em

from tandem.agent.models.peer import Peer
from tandem.agent.stores.peer import PeerStore
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolMessageType,
    InteragentProtocolUtils,
    PingBack,
    NewOperations,
    Bye,
)
from tandem.shared.protocol.handlers.base import ProtocolHandlerBase
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolHandler(ProtocolHandlerBase):
    def handle_message(self, retrieve_io_data):
        io_data = retrieve_io_data()
        super(InteragentProtocolHandler, self).handle_message(
            io_data.get_data(),
            io_data.get_address(),
        )

    @staticvalue
    def _protocol_message_utils(self):
        return InteragentProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            InteragentProtocolMessageType.Ping.value: self._handle_ping,
            InteragentProtocolMessageType.PingBack.value: self._handle_pingback,
            InteragentProtocolMessageType.Hello.value: self._handle_hello,
            InteragentProtocolMessageType.Bye.value: self._handle_bye,
            InteragentProtocolMessageType.NewOperations.value:
                self._handle_new_operations,
        }

    def __init__(self, std_streams, gateway, document):
        self._std_streams = std_streams
        self._gateway = gateway
        self._document = document
        self._next_editor_sequence = 0

    def _handle_ping(self, message, sender_address):
        io_data = self._gateway.generate_io_data(PingBack(), sender_address)
        self._gateway.write_io_data(io_data)

    def _handle_pingback(self, message, sender_address):
        pass

    def _handle_hello(self, message, sender_address):
        new_peer = Peer(sender_address)
        PeerStore.get_instance().add_peer(new_peer)

        # Send newly connected agent a copy of the document
        operations = self._document.get_document_operations()
        if len(operations) == 0:
            return

        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_list=json.dumps(operations)
        ))
        io_data = self._gateway.generate_io_data(
            payload,
            new_peer.get_address(),
        )
        self._gateway.write_io_data(io_data)

    def _handle_bye(self, message, sender_address):
        peer = PeerStore.get_instance().get_peer(sender_address)
        PeerStore.get_instance().remove_peer(peer)

    def _handle_new_operations(self, message, sender_address):
        operations_list = json.loads(message.operations_list)
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

    def stop(self):
        peers = PeerStore.get_instance().get_peers()
        io_data = self._gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Bye()),
            [peer.get_address() for peer in peers],
        )
        self._gateway.write_io_data(io_data)
        PeerStore.reset_instance()

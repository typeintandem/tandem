import logging
import json
import tandem.protocol.editor.messages as em
# import tandem.protocol.interagent.messages as im

from tandem.models.peer import Peer
from tandem.stores.peer import PeerStore
from tandem.protocol.interagent.messages import (
    InteragentProtocolMessageType,
    InteragentProtocolUtils,
    NewOperations,
    Bye,
)
from tandem.shared.protocol.handler.base import ProtocolHandlerBase
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolHandler(ProtocolHandlerBase):
    @staticvalue
    def _protocol_message_utils(self):
        return InteragentProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
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

    def _handle_hello(self, message, sender_address):
        new_peer = Peer(sender_address)
        PeerStore.get_instance().add_peer(new_peer)

        # Send newly connected agent a copy of the document
        operations = self._document.get_document_operations()
        if len(operations) == 0:
            return

        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_binary=json.dumps(operations)
        ))
        self._gateway.write_data(payload, new_peer.get_address())

    def _handle_bye(self, message, sender_address):
        peer = PeerStore.get_instance().get_peer(sender_address)
        PeerStore.get_instance().remove_peer(peer)

    def _handle_new_operations(self, message, sender_address):
        operations_list = json.loads(message.operations_binary)
        self._document.enqueue_remote_operations(operations_list)
        if not self._document.write_request_sent():
            self._std_streams.write_string_message(
                em.serialize(em.WriteRequest(self._next_editor_sequence)),
            )
            self._document.set_write_request_sent(True)
            logging.debug(
                "Sent write request seq: {}"
                .format(self._next_editor_sequence),
            )
            self._next_editor_sequence += 1

    def stop(self):
        peers = PeerStore.get_instance().get_peers()
        self._gateway.write_data(
            InteragentProtocolUtils.serialize(Bye()),
            [peer.get_address() for peer in peers],
        )
        PeerStore.reset_instance()

import logging
import json
import uuid
import tandem.agent.protocol.messages.editor as em

from tandem.agent.models.peer import DirectPeer
from tandem.agent.stores.peer import PeerStore
from tandem.agent.stores.pinging_peer import PingingPeerStore
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolMessageType,
    InteragentProtocolUtils,
    PingBack,
    NewOperations,
    Bye,
    Syn,
)
from tandem.agent.models.connection_state import ConnectionState
from tandem.agent.utils.hole_punching import HolePunchingUtils
from tandem.shared.protocol.handlers.base import ProtocolHandlerBase
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolHandler(ProtocolHandlerBase):
    @staticvalue
    def _protocol_message_utils(self):
        return InteragentProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            InteragentProtocolMessageType.Ping.value: self._handle_ping,
            InteragentProtocolMessageType.PingBack.value: self._handle_pingback,
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
        pinging_peer_store = PingingPeerStore.get_instance()
        peer_store = PeerStore.get_instance()

        pinging_peer = pinging_peer_store.get_peer(peer_id)
        regular_peer = peer_store.get_peer_by_id(peer_id)

        # Only reply to peers we know about to prevent the other
        # peer from thinking it can reach this peer successfully
        if pinging_peer is not None or regular_peer is not None:
            logging.debug(
                "Replying to ping from {} at {}:{}."
                .format(message.id, sender_address[0], sender_address[1]),
            )
            io_data = self._gateway.generate_io_data(
                InteragentProtocolUtils.serialize(PingBack(id=str(self._id))),
                sender_address,
            )
            self._gateway.write_io_data(io_data)

    def _handle_pingback(self, message, sender_address):
        peer_id = uuid.UUID(message.id)
        pinging_peer_store = PingingPeerStore.get_instance()
        pinging_peer = pinging_peer_store.get_peer(peer_id)
        if pinging_peer is None:
            return

        logging.debug(
            "Counting ping from {} at {}:{}."
            .format(message.id, sender_address[0], sender_address[1]),
        )
        pinging_peer.bump_ping_count(sender_address)
        promoted_peer = pinging_peer.maybe_promote_to_peer()
        if promoted_peer is None:
            return

        promoted_address = promoted_peer.get_address()
        logging.debug(
            "Promoted peer from {} with address {}:{}."
            .format(message.id, promoted_address[0], promoted_address[1]),
        )
        self._time_scheduler.cancel(pinging_peer.get_ping_handle())
        pinging_peer_store.remove_peer(pinging_peer)
        peer_store = PeerStore.get_instance()
        peer_store.add_peer(promoted_peer)

        if promoted_peer.get_connection_state() == ConnectionState.SEND_SYN:
            handle = self._time_scheduler.run_every(
                HolePunchingUtils.SYN_INTERVAL,
                HolePunchingUtils.send_syn,
                self._gateway,
                promoted_peer,
            )
            promoted_peer.append_handle(handle)

    def _handle_syn(self, message, sender_address):
        peer_store = PeerStore.get_instance()
        peer = peer_store.get_peer(sender_address)
        if peer is None or peer.get_connection_state() == ConnectionState.SEND_SYN:
            return
        peer.set_connection_state(ConnectionState.OPEN)
        for handle in peer.get_handles():
            self._time_scheduler.cancel(handle)
        peer.clear_handles()
        self._send_all_operations(peer, even_if_empty=True)
        peer_address = peer.get_address()
        logging.debug(
            "Connection to peer at {}:{} is open."
            .format(peer_address[0], peer_address[1]),
        )

    def _handle_hello(self, message, sender_address):
        new_peer = DirectPeer(sender_address)
        PeerStore.get_instance().add_peer(new_peer)
        self._send_all_operations(new_peer)

    def _handle_bye(self, message, sender_address):
        peer = PeerStore.get_instance().get_peer(sender_address)
        PeerStore.get_instance().remove_peer(peer)

    def _handle_new_operations(self, message, sender_address):
        peer_store = PeerStore.get_instance()
        peer = peer_store.get_peer(sender_address)
        if peer is not None and peer.get_connection_state() == ConnectionState.SEND_SYN:
            peer.set_connection_state(ConnectionState.OPEN)
            for handle in peer.get_handles():
                self._time_scheduler.cancel(handle)
            peer.clear_handles()
            peer_address = peer.get_address()
            logging.debug(
                "Connection to peer at {}:{} is open."
                .format(peer_address[0], peer_address[1]),
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

    def _send_all_operations(self, peer, even_if_empty=False):
        operations = self._document.get_document_operations()
        if not even_if_empty and len(operations) == 0:
            return

        payload = InteragentProtocolUtils.serialize(NewOperations(
            operations_list=json.dumps(operations)
        ))
        io_data = self._gateway.generate_io_data(
            payload,
            peer.get_address(),
        )
        self._gateway.write_io_data(io_data)

    def stop(self):
        peers = PeerStore.get_instance().get_peers()
        io_data = self._gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Bye()),
            [peer.get_address() for peer in peers],
        )
        self._gateway.write_io_data(io_data)
        PeerStore.reset_instance()

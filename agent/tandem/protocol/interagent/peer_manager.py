import json
from tandem.protocol.interagent.peer import Peer
import tandem.protocol.interagent.messages as im


class PeerManager:
    def __init__(self, gateway):
        self._peers = {}
        self._gateway = gateway
        self._next_operations_sequence = 0

    def register_peer(self, address):
        self._peers[address] = Peer(address)

    def remove_peer(self, address):
        del self._peers[address]

    def get_peer(self, address):
        if address not in self._peers:
            host, port = address
            raise ValueError(
                "Peer at {}:{} does not exist.".format(host, port))
        return self._peers[address]

    def broadcast_new_operations(self, operations_list):
        self._broadcast(self._operations_list_to_messages(operations_list))

    def send_operations_list(self, operations_list, address):
        self._send_messages(self._operations_list_to_messages(operations_list), address)

    def connect_to(self, host, port):
        address = (host, port)
        self._send_messages([im.Hello()], address)
        self.register_peer(address)

    def stop(self):
        self._broadcast([im.Bye()])

    def _operations_list_to_messages(self, operations_list):
        operations_json = json.dumps(operations_list)
        operations_binary = operations_json.encode("utf-8")

        if (len(operations_binary) + im.NewOperations.UNFRAGMENTED_HEADER_LENGTH
                <= self._gateway.max_payload_length()):
            return [im.NewOperations(operations_binary)]

        # The list of operations needs to be split into multiple messages
        # to accomdate UDP packet size limits
        operation_fragments = self._gateway.split_payload(
            operations_binary,
            im.NewOperations.FRAGMENTED_HEADER_LENGTH,
        )
        messages = im.NewOperations.from_fragmented_binary_operations(
            operation_fragments,
            self._next_operations_sequence,
        )
        self._next_operations_sequence += 1
        self._next_operations_sequence %= im.NewOperations.SEQUENCE_MOD
        return messages

    def _broadcast(self, messages):
        for address, _ in self._peers.items():
            for message in messages:
                self._gateway.write_binary_data(im.serialize(message), address)

    def _send_messages(self, messages, address):
        for message in messages:
            self._gateway.write_binary_data(im.serialize(message), address)

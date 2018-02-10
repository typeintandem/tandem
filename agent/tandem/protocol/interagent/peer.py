import tandem.protocol.interagent.messages as im


class NewOperationsFragments:
    def __init__(self, num_fragments):
        self._buffer = [None for _ in range(num_fragments)]
        self._fragments_left = num_fragments

    def integrate_new_operations_message(self, message):
        if self._buffer[message.fragment_number] is not None:
            # If a duplicate message
            return
        self._buffer[message.fragment_number] = message.operations_binary
        self._fragments_left -= 1

    def is_complete(self):
        return self._fragments_left <= 0

    def get_operations_binary(self):
        return b"".join(self._buffer)


class Peer:
    def __init__(self, address):
        self._address = address
        self._new_operations_fragments = {}

    def integrate_new_operations_message(self, message):
        if message.sequence_number not in self._new_operations_fragments:
            self._new_operations_fragments[message.sequence_number] = \
                NewOperationsFragments(message.total_fragments)

        fragments = self._new_operations_fragments[message.sequence_number]
        fragments.integrate_new_operations_message(message)

        if fragments.is_complete():
            operations_binary = fragments.get_operations_binary()
            del self._new_operations_fragments[message.sequence_number]
            return operations_binary

        return None

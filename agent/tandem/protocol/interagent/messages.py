import json
import enum

INTERAGENT_IDENTIFIER = b"\x54\x01"
INTERAGENT_HEADER_LENGTH = len(INTERAGENT_IDENTIFIER) + 2


class InteragentProtocolMarshalError(ValueError):
    pass


class InteragentProtocolMessageType(enum.Enum):
    NewOperations = int(0xA000)
    Hello = int(0xA00A)
    Bye = int(0xA00B)


class Hello:
    def __init__(self):
        self.type = InteragentProtocolMessageType.Hello

    def to_payload(self):
        return []

    @staticmethod
    def from_payload(payload):
        return Hello()


class Bye:
    def __init__(self):
        self.type = InteragentProtocolMessageType.Bye

    def to_payload(self):
        return []

    @staticmethod
    def from_payload(payload):
        return Bye()


class RawNewOperations:
    """
    Sent to other agents to notify them of new CRDT operations to apply.
    """
    def __init__(self, sequence_number, total_fragments, fragment_number, operations_binary):
        self.type = InteragentProtocolMessageType.NewOperations
        self.sequence_number = sequence_number
        self.total_fragments = total_fragments
        self.fragment_number = fragment_number
        self.operations_binary = operations_binary

    def is_fragmented(self):
        return self.total_fragments > 1

    def to_payload(self):
        payload_bytes = [
            self.sequence_number.to_bytes(2, byteorder="big"),
            self.total_fragments.to_bytes(2, byteorder="big"),
        ]
        if self.is_fragmented():
            payload_bytes.append(self.fragment_number.to_bytes(2, byteorder="big"))
        payload_bytes.append(self.operations_binary)
        return payload_bytes

    @staticmethod
    def from_payload(payload):
        sequence_number = int.from_bytes(payload[0:2], byteorder="big")
        total_fragments = int.from_bytes(payload[2:4], byteorder="big")
        fragment_number = 0
        if total_fragments > 1:
            fragment_number = int.from_bytes(payload[4:6], byteorder="big")
        data_offset = 6 if total_fragments > 1 else 4

        return RawNewOperations(sequence_number, total_fragments, fragment_number, payload[data_offset:])


def serialize(message):
    binary_parts = [INTERAGENT_IDENTIFIER]
    binary_parts.append(message.type.value.to_bytes(2, byteorder="big"))
    binary_parts.extend(message.to_payload())
    return b"".join(binary_parts)


def deserialize(data):
    if len(data) < INTERAGENT_HEADER_LENGTH or data[0:2] != INTERAGENT_IDENTIFIER:
        raise InteragentProtocolMarshalError

    message_type = int.from_bytes(data[2:4], byteorder="big")
    payload = data[4:]

    if message_type == InteragentProtocolMessageType.Hello.value:
        return Hello.from_payload(payload)

    elif message_type == InteragentProtocolMessageType.Bye.value:
        return Bye.from_payload(payload)

    elif message_type == InteragentProtocolMessageType.NewOperations.value:
        return RawNewOperations.from_payload(payload)

    else:
        raise InteragentProtocolMarshalError

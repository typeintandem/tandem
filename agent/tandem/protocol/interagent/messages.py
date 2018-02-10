import json
import enum

# Interagent messages are prefixed with "T" in UTF-8 encoding (0x54)
# followed by an 8-bit protocol version number.
HEADER = b"\x54\x01"

# Version 1 messages contain a 16-bit message identifier that follows
# the header. So all messages are at least 4 bytes long.
MIN_MESSAGE_LENGTH = len(HEADER) + 2


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


class NewOperations:
    """
    Sent to other agents to notify them of new CRDT operations to apply.

    This message could have multiple fragments if the operations payload is too large.
    If there are multiple fragments, the message will contain a sequence number and
    fragment number.

    All fragments in the same message share the same sequence number. The fragment number
    is used to order the payloads when reassembling the message.
    """

    SEQUENCE_MAX = int(0xFFFF)
    SEQUENCE_MOD = SEQUENCE_MAX + 1

    UNFRAGMENTED_HEADER_LENGTH = MIN_MESSAGE_LENGTH + 2
    FRAGMENTED_HEADER_LENGTH = MIN_MESSAGE_LENGTH + 4

    def __init__(self, operations_binary, total_fragments=1, sequence_number=None, fragment_number=None):
        self.type = InteragentProtocolMessageType.NewOperations
        self.operations_binary = operations_binary
        self.sequence_number = sequence_number
        self.total_fragments = total_fragments
        self.fragment_number = fragment_number

    def is_fragmented(self):
        return self.total_fragments > 1

    def to_payload(self):
        payload_bytes = [self.total_fragments.to_bytes(2, byteorder="big")]
        if self.is_fragmented():
            payload_bytes.append(self.sequence_number.to_bytes(2, byteorder="big"))
            payload_bytes.append(self.fragment_number.to_bytes(2, byteorder="big"))
        payload_bytes.append(self.operations_binary)
        return payload_bytes

    @staticmethod
    def from_payload(payload):
        total_fragments = int.from_bytes(payload[0:2], byteorder="big")

        if total_fragments == 1:
            return NewOperations(payload[2:])

        sequence_number = int.from_bytes(payload[2:4], byteorder="big")
        fragment_number = int.from_bytes(payload[4:6], byteorder="big")
        return NewOperations(
            payload[6:],
            total_fragments,
            sequence_number,
            fragment_number,
        )

    @staticmethod
    def from_fragmented_binary_operations(fragments, sequence_number):
        messages = []
        total_fragments = len(fragments)
        for fragment_number in range(total_fragments):
            messages.append(NewOperations(
                fragments[fragment_number],
                total_fragments,
                sequence_number,
                fragment_number,
            ))
        return messages


def serialize(message):
    binary_parts = [HEADER]
    binary_parts.append(message.type.value.to_bytes(2, byteorder="big"))
    binary_parts.extend(message.to_payload())
    return b"".join(binary_parts)


def deserialize(data):
    if len(data) < MIN_MESSAGE_LENGTH or data[0:2] != HEADER:
        raise InteragentProtocolMarshalError

    message_type = int.from_bytes(data[2:4], byteorder="big")
    payload = data[4:]

    if message_type == InteragentProtocolMessageType.Hello.value:
        return Hello.from_payload(payload)

    elif message_type == InteragentProtocolMessageType.Bye.value:
        return Bye.from_payload(payload)

    elif message_type == InteragentProtocolMessageType.NewOperations.value:
        return NewOperations.from_payload(payload)

    else:
        raise InteragentProtocolMarshalError

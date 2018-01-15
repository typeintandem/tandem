import json
import enum


class InteragentProtocolMarshalError(ValueError):
    pass


class InteragentProtocolMessageType(enum.Enum):
    TextChanged = "text-changed"
    Ping = "ping"
    NewOperations = "new-operations"


class TextChanged:
    """
    Sent to other agents to notify them that the text buffer has been changed.
    """
    def __init__(self, contents):
        self.type = InteragentProtocolMessageType.TextChanged
        self.contents = contents

    def to_payload(self):
        return {
            "contents": self.contents,
        }

    @staticmethod
    def from_payload(payload):
        return TextChanged(payload["contents"])


class Ping:
    """
    Sent between agents for testing purposes.
    """
    def __init__(self, ttl):
        self.type = InteragentProtocolMessageType.Ping
        self.ttl = ttl

    def to_payload(self):
        return {
            "ttl": self.ttl,
        }

    @staticmethod
    def from_payload(payload):
        return Ping(payload["ttl"])


class NewOperations:
    """
    Sent to other agents to notify them of new CRDT operations to apply.

    The value of operations_list should be passed as-is to the document's
    apply_operations() function. The patches that are returned by that
    call should be passed to the plugin using the ApplyPatches editor
    protocol message.
    """
    def __init__(self, operations_list):
        self.type = InteragentProtocolMessageType.NewOperations
        self.operations_list = operations_list

    def to_payload(self):
        return {
            "operations_list": self.operations_list,
        }

    @staticmethod
    def from_payload(payload):
        return NewOperations(payload["operations_list"])


def serialize(message):
    as_dict = {
        "type": message.type.value,
        "payload": message.to_payload(),
        "version": 1,
    }
    return json.dumps(as_dict)


def deserialize(data):
    try:
        as_dict = json.loads(data)
        message_type = as_dict["type"]
        payload = as_dict["payload"]

        if message_type == InteragentProtocolMessageType.TextChanged.value:
            return TextChanged.from_payload(payload)

        elif message_type == InteragentProtocolMessageType.Ping.value:
            return Ping.from_payload(payload)

        elif message_type == InteragentProtocolMessageType.NewOperations.value:
            return NewOperations.from_payload(payload)

        else:
            raise InteragentProtocolMarshalError

    except json.JSONDecodeError:
        raise InteragentProtocolMarshalError

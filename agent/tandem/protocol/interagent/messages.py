import json
import enum


class InteragentProtocolMarshalError:
    pass


class InteragentProtocolMessageType(enum.Enum):
    TextChanged = "text-changed"
    Ping = "ping"


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
        type = as_dict["type"]
        payload = as_dict["payload"]

        if type == InteragentProtocolMessageType.TextChanged.value:
            return TextChanged.from_payload(payload)

        elif type == InteragentProtocolMessageType.Ping.value:
            return Ping.from_payload(payload)

        else:
            raise InteragentProtocolMarshalError

    except JSONDecodeError:
        raise InteragentProtocolMarshalError

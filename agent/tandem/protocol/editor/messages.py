import json
import enum


class EditorProtocolMarshalError(ValueError):
    pass


class EditorProtocolMessageType(enum.Enum):
    UserChangedEditorText = "user-changed-editor-text"
    ApplyText = "apply-text"
    ConnectTo = "connect-to"


class UserChangedEditorText:
    """
    Sent by the editor plugin to the agent to
    notify it that the user changed the text buffer.
    """
    def __init__(self, contents):
        self.type = EditorProtocolMessageType.UserChangedEditorText
        self.contents = contents

    def to_payload(self):
        return {
            "contents": self.contents,
        }

    @staticmethod
    def from_payload(payload):
        return UserChangedEditorText(payload["contents"])


class ApplyText:
    """
    Sent by the agent to the editor plugin to
    notify it that someone else edited the text buffer.
    """
    def __init__(self, contents):
        self.type = EditorProtocolMessageType.ApplyText
        self.contents = contents

    def to_payload(self):
        return {
            "contents": self.contents,
        }

    @staticmethod
    def from_payload(payload):
        return ApplyText(payload["contents"])


class ConnectTo:
    """
    Sent by the plugin to the agent to tell it to connect
    to another agent.
    """
    def __init__(self, host, port):
        self.type = EditorProtocolMessageType.ConnectTo
        self.host = host
        self.port = port

    def to_payload(self):
        return {
            "host": self.host,
            "port": self.port,
        }

    @staticmethod
    def from_payload(payload):
        return ConnectTo(payload["host"], payload["port"])


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

        if type == EditorProtocolMessageType.ConnectTo.value:
            return ConnectTo.from_payload(payload)

        elif type == EditorProtocolMessageType.UserChangedEditorText.value:
            return UserChangedEditorText.from_payload(payload)

        elif type == EditorProtocolMessageType.ApplyTextBuffer.value:
            return ApplyTextBuffer.from_payload(payload)

        else:
            raise EditorProtocolMarshalError

    except json.JSONDecodeError:
        raise EditorProtocolMarshalError

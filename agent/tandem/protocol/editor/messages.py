import json
import enum


class EditorProtocolMarshalError:
    pass


class EditorProtocolMessageType(enum.Enum):
    UserChangedEditorText = "user-changed-editor-text"
    ApplyText = "apply-text"


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

        if type == EditorProtocolMessageType.UserChangedEditorText.value:
            return UserChangedEditorText.from_payload(payload)

        elif type == EditorProtocolMessageType.ApplyTextBuffer.value:
            return ApplyTextBuffer.from_payload(payload)

        else:
            raise EditorProtocolMarshalError

    except JSONDecodeError:
        raise EditorProtocolMarshalError

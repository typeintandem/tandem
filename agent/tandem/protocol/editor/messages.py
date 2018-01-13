import json
import enum


class EditorProtocolMarshalError(ValueError):
    pass


class EditorProtocolMessageType(enum.Enum):
    UserChangedEditorText = "user-changed-editor-text"
    ApplyText = "apply-text"
    ConnectTo = "connect-to"
    NewPatches = "new-patches"
    ApplyPatches = "apply-patches"


class UserChangedEditorText:

    """
    Sent by the editor plugin to the agent to
    notify it that the user changed the text buffer.
    """
    def __init__(self, contents):
        # self.__guard__(contents)

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
        # self.__guard__(contents)

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


class NewPatches:
    """
    Sent by the plugin to the agent to inform it of text buffer patches.
    start: {row, col}
    end: {row, col}
    text: ""
    """
    def __init__(self, patch_list):
        self.type = EditorProtocolMessageType.NewPatches
        self.patch_list = patch_list

    def to_payload(self):
        return {
            "patch_list": self.patch_list
        }

    @staticmethod
    def from_payload(payload):
        return NewPatches(payload["patch_list"])


class ApplyPatches:
    def __init__(self, patch_list):
        self.type = EditorProtocolMessageType.ApplyPatches
        self.patch_list = patch_list

    def to_payload(self):
        return {
            "patch_list": self.patch_list
        }

    @staticmethod
    def from_payload(payload):
        return ApplyPatches(payload["patch_list"])


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

        if message_type == EditorProtocolMessageType.ConnectTo.value:
            return ConnectTo.from_payload(payload)

        elif message_type == \
                EditorProtocolMessageType.UserChangedEditorText.value:
            return UserChangedEditorText.from_payload(payload)

        elif message_type == EditorProtocolMessageType.ApplyText.value:
            return ApplyText.from_payload(payload)

        elif message_type == EditorProtocolMessageType.NewPatches.value:
            return NewPatches.from_payload(payload)

        elif message_type == EditorProtocolMessageType.ApplyPatches.value:
            return ApplyPatches.from_payload(payload)

        else:
            raise EditorProtocolMarshalError

    except:
        raise EditorProtocolMarshalError

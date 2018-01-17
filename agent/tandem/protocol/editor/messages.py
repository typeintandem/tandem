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


class CheckDocumentSync:

    """
    Sent by the editor plugin to the agent to
    check whether the editor and the crdt have their
    document contents in sync
    """

    def __init__(self, contents):
        # self.__guard__(contents)

        self.type = EditorProtocolMessageType.CheckDocumentSync
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
    Sent by the plugin to the agent to inform it of changes made by
    the user to their local text buffer.

    patch_list should be a list of dictionaries where each dictionary
    represents a change that the user made to their local text buffer.
    The patches should be ordered such that they are applied in the
    correct order when the list is traversed from front to back.

    Each patch should have the form:

    {
        "start": {"row": <row>, "column": <column>},
        "end": {"row": <row>, "column": <column>},
        "text": <text>,
    }
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
    """
    Sent by the agent to the plugin to inform it of remote changes
    that should be applied to their local text buffer.

    patch_list will be a list of dictionaries where each dictionary
    represents a change that some remote user made to the text buffer.
    The order of the patches is significant. They should applied in
    the order they are found in this message.

    Each patch will have the form:

    {
        "oldStart": {"row": <row>, "column": <column>},
        "oldEnd": {"row": <row>, "column": <column>},
        "oldText": <old text>,
        "newStart": {"row": <row>, "column": <column>},
        "newEnd": {"row": <row>, "column": <column>},
        "newText": <new text>,
    }
    """
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

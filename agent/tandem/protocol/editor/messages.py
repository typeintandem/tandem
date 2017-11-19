import json


class EditorProtocolMarshalError:
    pass


def serialize(message):
    return json.dumps(message)


def deserialize(data):
    try:
        return json.loads(data)
    except JSONDecodeError:
        raise EditorProtocolMarshalError

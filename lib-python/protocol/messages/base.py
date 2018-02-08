import json
import enum


class ProtocolMarshalError(ValueError):
    pass


class ProtocolMessageTypeBase(enum.Enum):
    pass


class ProtocolMessageBase(object):
    def __init__(self, message_type, payload):
        for key in self._payload_keys():
            setattr(self, key, payload.get(key, None))
        self.type = message_type

    def to_payload(self):
        return {key: getattr(self, key, None) for key in self._payload_keys()}

    def _payload_keys(self):
        return []


class ProtocolUtilsBase(object):
    @staticmethod
    def serialize(message):
        as_dict = {
            "type": message.type.value,
            "payload": message.to_payload(),
            "version": 1,
        }
        return json.dumps(as_dict)

    @staticmethod
    def _deserialize(message_types, data):
        try:
            as_dict = json.loads(data)
            as_dict = json.loads(as_dict)
            data_message_type = as_dict["type"]
            data_payload = as_dict["payload"]

            for message_type, constructor in message_types.items():
                if message_type == data_message_type:
                    return constructor(data_payload)

            raise RendezvousProtocolMarshalError

        except json.JSONDecodeError:
            raise RendezvousProtocolMarshalError

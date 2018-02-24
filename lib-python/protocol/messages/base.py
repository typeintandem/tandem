import json
import enum


class ProtocolMarshalError(ValueError):
    pass


class ProtocolMessageTypeBase(enum.Enum):
    pass


class ProtocolMessageBase(object):
    def __init__(self, message_type, **kwargs):
        for key in self._payload_keys():
            setattr(self, key, kwargs.get(key, None))

        self.type = message_type

    def _payload_keys(self):
        return None

    def to_payload(self):
        return {key: getattr(self, key, None) for key in self._payload_keys()}

    @classmethod
    def from_payload(cls, **kwargs):
        return cls(**kwargs)


class ProtocolUtilsBase(object):
    @classmethod
    def _protocol_message_constructors(cls):
        return None

    @staticmethod
    def serialize(message):
        as_dict = {
            "type": message.type.value,
            "payload": message.to_payload(),
            "version": 1,
        }
        return json.dumps(as_dict)

    @classmethod
    def deserialize(cls, as_dict):
        data_message_type = as_dict["type"]
        data_payload = as_dict["payload"]
        items = cls._protocol_message_constructors().items()

        for message_type, target_class in items:
            if message_type == data_message_type:
                return target_class.from_payload(**data_payload)

        raise ProtocolMarshalError

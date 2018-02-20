import logging
import json
from tandem.shared.protocol.messages.base import ProtocolMarshalError


class ProtocolHandlerBase(object):
    def _protocol_message_utils(self):
        return None

    def _protocol_message_handlers(self):
        return None

    def _raw_data_to_dict(self, data):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ProtocolMarshalError

    def handle_raw_data(self, data, sender_address):
        try:
            as_dict = self._raw_data_to_dict(data)
            handled = self.handle_message(as_dict, sender_address)

            if not handled:
                logging.info(
                    "Protocol message was not handled. Deserialization"
                    "failed or no handler was registered.",
                )

        except ProtocolMarshalError:
            logging.info(
                "Protocol message was ignored because it was not valid JSON.",
            )

        except:
            logging.exception("Exception when handling protocol message:")
            raise

    def handle_message(self, message_as_dict, sender_address):
        try:
            message = \
                self._protocol_message_utils().deserialize(message_as_dict)
            items = self._protocol_message_handlers().items()

            for message_type, handler in items:
                if message_type == message.type.value:
                    handler(message, sender_address)
                    return True

            return False

        except ProtocolMarshalError:
            return False

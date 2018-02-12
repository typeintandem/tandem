import logging
from tandem.shared.protocol.messages.base import ProtocolMarshalError


class ProtocolHandlerBase(object):
    def _protocol_message_utils(self):
        return None

    def _protocol_message_handlers(self):
        return None

    def handle_message(self, data, sender_address):
        try:
            message = self._protocol_message_utils().deserialize(data)
            items = self._protocol_message_handlers().items()

            for message_type, handler in items:
                if message_type == message.type.value:
                    handler(message, sender_address)

        except ProtocolMarshalError:
            logging.info("Ignoring invalid protocol message.")

        except:
            logging.exception("Exception when handling protocol message:")
            raise

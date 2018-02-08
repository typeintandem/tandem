import logging
from tandem.shared.protocol.messages.base import ProtocolMarshalError


class ProtocolHandlerBase(object):
    @staticmethod
    def handle_message(utils, message_types, data, sender_address):
        try:
            message = utils.deserialize(data)

            for message_type, handler in message_types.items():
                if message_type == message.type.value:
                    handler(message, sender_address)

        except ProtocolMarshalError:
            logging.info("Ignoring invalid protocol message.")

        except:
            logging.exception("Exception when handling protocol message:")
            raise

import logging
import json
from tandem.shared.protocol.messages.base import ProtocolMarshalError


class ProtocolHandlerBase(object):
    def _protocol_message_utils(self):
        return None

    def _protocol_message_handlers(self):
        return None

    def _extra_handler_arguments(self, io_data):
        return []

    def handle_raw_data(self, retrieve_io_data):
        try:
            io_data = retrieve_io_data()
            if io_data is None or io_data.is_empty():
                return

            data_as_dict = json.loads(io_data.get_data())
            handled = self.handle_message(data_as_dict, io_data)

            if not handled:
                logging.info(
                    "Protocol message was not handled because "
                    "no handler was registered.",
                )

        except json.JSONDecodeError:
            logging.info(
                "Protocol message was ignored because it was not valid JSON.",
            )

        except:
            logging.exception("Exception when handling protocol message:")
            raise

    def handle_message(self, data_as_dict, io_data):
        try:
            message = \
                self._protocol_message_utils().deserialize(data_as_dict)
            items = self._protocol_message_handlers().items()

            for message_type, handler in items:
                if message_type == message.type.value:
                    handler(message, *self._extra_handler_arguments(io_data))
                    return True

            return False

        except ProtocolMarshalError:
            return False

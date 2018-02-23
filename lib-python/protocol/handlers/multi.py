from tandem.shared.protocol.handlers.base import ProtocolHandlerBase


class MultiProtocolHandler(ProtocolHandlerBase):
    def __init__(self, *handlers):
        self._handlers = [handler for handler in handlers]

    def handle_message(self, data_as_dict, io_data):
        for handler in self._handlers:
            handled = handler.handle_message(data_as_dict, io_data)
            if handled:
                return True

        return False

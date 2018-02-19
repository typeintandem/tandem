from tandem.shared.protocol.handlers.base import ProtocolHandlerBase


class CombinedProtocolHandler(ProtocolHandlerBase):
    def __init__(self, *handlers):
        self._handlers = [handler for handler in handlers]

    def handle_message(self, message_as_dict, sender_address):
        for handler in self._handlers:
            handled = handler.handle_message(message_as_dict, sender_address)
            if handled:
                return True

        return False

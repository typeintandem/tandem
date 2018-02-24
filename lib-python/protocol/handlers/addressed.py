from tandem.shared.protocol.handlers.base import ProtocolHandlerBase


class AddressedHandler(ProtocolHandlerBase):
    def _extra_handler_arguments(self, io_data):
        return [io_data.get_address()]

from tandem.shared.io.proxies.base import ProxyBase


class UnicodeProxy(ProxyBase):
    def pre_generate_io_data(self, params):
        args, kwargs = params
        messages, addresses = args
        encoded_messages = [
            message.encode("utf-8") if hasattr(message, "encode") else message
            for message in messages
        ]
        return ((encoded_messages, addresses), kwargs)

    def on_retrieve_io_data(self, params):
        args, kwargs = params
        if args is None:
            return params

        raw_data, address = args
        data = (
            raw_data.decode("utf-8") if hasattr(raw_data, "decode")
            else raw_data
        )
        return ((data, address), kwargs)

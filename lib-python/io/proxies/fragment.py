from tandem.shared.io.proxies.base import ProxyBase
from tandem.shared.utils.fragment import FragmentUtils


class FragmentProxy(ProxyBase):
    def __init__(self, max_message_length=512):
        self._max_message_length = max_message_length

    def pre_generate_io_data(self, params):
        args, kwargs = params
        messages, addresses = args

        if type(messages) is not list:
            messages = [messages]

        new_messages = []
        for message in messages:
            should_fragment = FragmentUtils.should_fragment(
                message,
                self._max_message_length,
            )
            if should_fragment:
                new_messages.extend(FragmentUtils.fragment(
                    message,
                    self._max_message_length,
                ))
            else:
                new_messages.append(message)

        new_args = (new_messages, addresses)
        return (new_args, kwargs)

    def on_retrieve_io_data(self, params):
        args, kwargs = params
        if args is None or args is (None, None):
            return params

        raw_data, address = args

        if FragmentUtils.is_fragment(raw_data):
            defragmented_data = FragmentUtils.defragment(raw_data, address)
            if defragmented_data:
                new_args = (defragmented_data, address)
                return (new_args, kwargs)
            else:
                return (None, None)
        else:
            return params

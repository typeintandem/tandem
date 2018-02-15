from tandem.agent.io.udp_gateway import UDPData, UDPGateway
from tandem.agent.utils.fragment import FragmentUtils


class FragmentedUDPData(UDPData):
    pass


class FragmentedUDPGateway(UDPGateway):
    def generate_io_data(self, messages, addresses):
        if type(messages) is not list:
            messages = [messages]

        new_messages = []
        for message in messages:
            if FragmentUtils.should_fragment(message):
                new_messages.extend(FragmentUtils.fragment(message))
            else:
                new_messages.append(message)

        return super(FragmentedUDPGateway, self).generate_io_data(
            new_messages,
            addresses,
        )

    def _received_data(self, io_data):
        raw_data = io_data.get_data()
        address = io_data.get_address()

        if FragmentUtils.is_fragment(raw_data):
            defragmented_data = FragmentUtils.defragment(raw_data, address)
            if defragmented_data:
                new_data = FragmentedUDPData(defragmented_data, address)
                super(FragmentedUDPGateway, self)._received_data(new_data)
        else:
            super(FragmentedUDPGateway, self)._received_data(io_data)

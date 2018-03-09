from tandem.shared.io.proxies.base import ProxyBase
from tandem.shared.utils.relay import RelayUtils
from tandem.shared.io.udp_gateway import UDPGateway
from tandem.agent.stores.connection import ConnectionStore


class AgentRelayProxy(ProxyBase):
    def __init__(self, relay_server_address):
        self._relay_server_address = relay_server_address

    def should_relay(self, address):
        connection_store = ConnectionStore.get_instance()
        connection = connection_store.get_connection_by_address(address)
        return (
            self._relay_server_address != address and
            connection and connection.is_relayed()
        )

    def pre_write_io_data(self, params):
        args, kwargs = params
        io_datas, = args

        new_io_datas = []
        for io_data in io_datas:
            new_io_data = io_data
            if self.should_relay(io_data.get_address()):
                new_raw_data = RelayUtils.serialize(
                    io_data.get_data(),
                    io_data.get_address(),
                )
                new_io_data = UDPGateway.data_class(
                    new_raw_data,
                    self._relay_server_address,
                )
            new_io_datas.append(new_io_data)

        new_args = (new_io_datas,)
        return (new_args, kwargs)

    def on_retrieve_io_data(self, params):
        args, kwargs = params
        if args is None or args is (None, None):
            return params

        raw_data, address = args

        if RelayUtils.is_relay(raw_data):
            new_data, new_address = RelayUtils.deserialize(raw_data)
            new_args = new_data, new_address
            return (new_args, kwargs)
        else:
            return params

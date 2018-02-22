from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    Ping,
    PingBack,
    Syn,
)


class HolePunchingUtils:
    PING_INTERVAL = 0.15
    SYN_INTERVAL = 0.15

    @staticmethod
    def send_ping(gateway, addresses, id):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Ping(id=str(id))),
            addresses
        )
        gateway.write_io_data(io_data)

    @staticmethod
    def send_pingback(gateway, address, id):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(PingBack(id=str(id))),
            address,
        )
        gateway.write_io_data(io_data)

    @staticmethod
    def send_syn(gateway, address):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Syn()),
            address,
        )
        gateway.write_io_data(io_data)

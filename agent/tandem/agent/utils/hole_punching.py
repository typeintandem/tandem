from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    Ping,
    PingBack,
    Syn,
)


class HolePunchingUtils:
    PING_INTERVAL=0.1
    SYN_INTERVAL=0.1

    @staticmethod
    def send_ping(gateway, peer, id):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Ping(id=str(id))),
            peer.get_addresses(),
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
    def send_syn(gateway, peer):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(Syn()),
            peer.get_address(),
        )
        gateway.write_io_data(io_data)

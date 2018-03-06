from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    Ping,
    Syn,
)


class HolePunchingUtils:
    PING_INTERVAL = 0.15
    SYN_INTERVAL = 0.15
    TIMEOUT = 3

    @staticmethod
    def generate_send_ping(gateway, addresses, id):
        def send_ping():
            HolePunchingUtils._send_message(
                gateway,
                addresses,
                Ping(id=str(id)),
            )
        return send_ping

    @staticmethod
    def generate_send_syn(gateway, address):
        def send_syn():
            HolePunchingUtils._send_message(
                gateway,
                address,
                Syn(),
            )
        return send_syn

    @staticmethod
    def _send_message(gateway, addresses, message):
        io_data = gateway.generate_io_data(
            InteragentProtocolUtils.serialize(message),
            addresses,
        )
        gateway.write_io_data(io_data)

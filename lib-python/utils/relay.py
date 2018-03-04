class RelayUtils(object):
    HEADER = b"\x54\x01"
    RELAY_HEADER = b"\x52\x45"

    @classmethod
    def is_relay(cls, raw_data):
        return (
            raw_data[0:2] == cls.HEADER and
            raw_data[2:4] == cls.RELAY_HEADER
        )

    @staticmethod
    def serialize(payload, address):
        result = []
        ip, port = address
        ip_binary = map(
            lambda x: (int(x)).to_bytes(1, byteorder="big"),
            ip.split("."),
        )

        result.append(RelayUtils.HEADER)
        result.append(RelayUtils.RELAY_HEADER)
        result.extend(ip_binary)
        result.append(port.to_bytes(2, byteorder="big"))
        result.append(payload)

        return b"".join(result)

    @staticmethod
    def deserialize(raw_data):
        ip = ".".join([
            str(int.from_bytes(raw_data[4:5], byteorder="big")),
            str(int.from_bytes(raw_data[5:6], byteorder="big")),
            str(int.from_bytes(raw_data[6:7], byteorder="big")),
            str(int.from_bytes(raw_data[7:8], byteorder="big")),
        ])
        port = int.from_bytes(raw_data[8:10], byteorder="big")

        address = (ip, port)
        payload = raw_data[10:]

        return payload, address

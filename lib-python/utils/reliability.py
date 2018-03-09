from tandem.shared.stores.reliability import ReliabilityStore


class ReliabilityUtils(object):
    HEADER = b"\x54\x01"
    RELIABILITY_HEADER = b"\x52\x4C"
    ACK_HEADER = b"\x41\x43"
    ACK_TIMEOUT = 3

    MAX_ACK_NUMBER = int(0xFFFF)
    next_ack_number = -1

    @classmethod
    def get_next_ack_number(cls):
        cls.next_ack_number += 1
        cls.next_ack_number %= cls.MAX_ACK_NUMBER + 1

        return cls.next_ack_number

    @classmethod
    def is_ack(cls, raw_data):
        return (
            raw_data[0:2] == cls.HEADER and
            raw_data[2:4] == cls.ACK_HEADER
        )

    @classmethod
    def is_ackable(cls, raw_data):
        return (
            raw_data[0:2] == cls.HEADER and
            raw_data[2:4] == cls.RELIABILITY_HEADER
        )

    @staticmethod
    def should_resend_payload(ack_id):
        return ReliabilityStore.get_instance().get_payload(ack_id)

    @staticmethod
    def generate_ack(ack_id):
        result = []
        result.append(ReliabilityUtils.HEADER)
        result.append(ReliabilityUtils.ACK_HEADER)
        result.append((ack_id).to_bytes(2, byteorder="big"))
        return b"".join(result)

    @staticmethod
    def parse_ack(raw_data):
        return int.from_bytes(raw_data[4:6], byteorder="big")

    @staticmethod
    def serialize(payload):
        result = []
        ack_number = ReliabilityUtils.get_next_ack_number()
        result.append(ReliabilityUtils.HEADER)
        result.append(ReliabilityUtils.RELIABILITY_HEADER)
        result.append(ack_number.to_bytes(2, byteorder="big"))
        result.append(payload)
        return b"".join(result), ack_number

    @staticmethod
    def deserialize(raw_data):
        ack_id = int.from_bytes(raw_data[4:6], byteorder="big")
        payload = raw_data[6:]
        return payload, ack_id

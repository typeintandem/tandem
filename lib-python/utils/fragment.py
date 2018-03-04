from tandem.shared.stores.fragment import FragmentStore
from tandem.shared.models.fragment import Fragment


class FragmentUtils(object):
    HEADER = b"\x54\x01"
    FRAGMENT_HEADER = b"\x46\x52"
    FRAGMENT_HEADER_LENGTH = len(HEADER) + len(FRAGMENT_HEADER) + 6

    MAX_SEQUENCE_NUMBER = int(0xFFFF)
    next_sequence_number = -1

    @classmethod
    def is_fragment(cls, message):
        return (
            message[0:2] == cls.HEADER and
            message[2:4] == cls.FRAGMENT_HEADER
        )

    @staticmethod
    def should_fragment(message, max_message_length):
        return len(message) > max_message_length

    @classmethod
    def get_next_sequence_number(cls):
        cls.next_sequence_number += 1
        cls.next_sequence_number %= cls.MAX_SEQUENCE_NUMBER + 1

        return cls.next_sequence_number

    @staticmethod
    def serialize(fragment, sequence_number):
        result = []
        result.append(FragmentUtils.HEADER)
        result.append(FragmentUtils.FRAGMENT_HEADER)
        result.append(
            fragment.get_total_fragments().to_bytes(2, byteorder="big")
        )
        result.append(
            sequence_number.to_bytes(2, byteorder="big")
        )
        result.append(
            fragment.get_fragment_number().to_bytes(2, byteorder="big")
        )
        result.append(fragment.get_payload())
        return b"".join(result)

    @staticmethod
    def deserialize(message):
        total_fragments = int.from_bytes(message[4:6], byteorder="big")
        sequence_number = int.from_bytes(message[6:8], byteorder="big")
        fragment_number = int.from_bytes(message[8:10], byteorder="big")
        payload = message[10:]

        new_fragment = Fragment(total_fragments, fragment_number, payload)
        return new_fragment, sequence_number

    @classmethod
    def fragment(cls, payload, max_message_length):
        max_payload_length = max_message_length - cls.FRAGMENT_HEADER_LENGTH

        payloads = [
            payload[i:i + max_payload_length]
            for i in range(0, len(payload), max_payload_length)
        ]

        fragments = [
            Fragment(len(payloads), index, payload)
            for index, payload in enumerate(payloads)
        ]

        sequence_number = FragmentUtils.get_next_sequence_number()
        messages = [
            FragmentUtils.serialize(fragment, sequence_number)
            for fragment in fragments
        ]

        return messages

    @staticmethod
    def defragment(raw_data, sender_address):
        fragment_store = FragmentStore.get_instance()
        fragment, sequence_number = FragmentUtils.deserialize(raw_data)
        fragment_store.insert_fragment(
            sender_address,
            sequence_number,
            fragment
        )
        fragment_group = fragment_store.get_fragment_group(
            sender_address,
            sequence_number,
        )

        defragmented_data = fragment_group.defragment()
        if fragment_group.is_complete():
            fragment_store.remove_fragment_group(
                sender_address,
                sequence_number,
            )
        return defragmented_data

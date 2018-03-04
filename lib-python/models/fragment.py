from tandem.shared.models.base import ModelBase


class Fragment(ModelBase):
    def __init__(
        self,
        total_fragments,
        fragment_number,
        payload,
    ):
        self._total_fragments = total_fragments
        self._fragment_number = fragment_number
        self._payload = payload

    def get_total_fragments(self):
        return self._total_fragments

    def get_fragment_number(self):
        return self._fragment_number

    def get_payload(self):
        return self._payload


class FragmentGroup(ModelBase):
    def __init__(self, total_fragments):
        self._total_fragments = total_fragments
        self._buffer = [None for _ in range(total_fragments)]

    def add_fragment(self, fragment):
        fragment_number = fragment.get_fragment_number()
        if self._buffer[fragment_number] is None:
            self._buffer[fragment_number] = fragment.get_payload()

    def is_complete(self):
        non_empty_fragments = list(filter(lambda x: x, self._buffer))
        return len(non_empty_fragments) >= self._total_fragments

    def defragment(self):
        return b"".join(self._buffer) if self.is_complete() else None

from tandem.shared.models.fragment import FragmentGroup
from tandem.shared.stores.base import StoreBase


class FragmentStore(StoreBase):
    def __init__(self):
        self._peer_fragment_groups = {}

    def insert_fragment(self, address, message_id, fragment):
        if address not in self._peer_fragment_groups:
            self._peer_fragment_groups[address] = {}

        fragment_groups = self._peer_fragment_groups[address]
        if message_id not in fragment_groups:
            new_group = FragmentGroup(fragment.get_total_fragments())
            fragment_groups[message_id] = new_group

        fragment_groups[message_id].add_fragment(fragment)

    def get_fragment_group(self, address, message_id):
        return self._peer_fragment_groups[address][message_id]

    def remove_fragment_group(self, address, message_id):
        del self._peer_fragment_groups[address][message_id]

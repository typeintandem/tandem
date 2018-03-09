from tandem.shared.stores.base import StoreBase


class ReliabilityStore(StoreBase):
    def __init__(self):
        self._payloads = {}

    def add_payload(self, payload_id, payload):
        self._payloads[payload_id] = payload

    def get_payload(self, payload_id):
        return self._payloads.get(payload_id, None)

    def remove_payload(self, payload_id):
        if payload_id in self._payloads:
            del self._payloads[payload_id]

from tandem.shared.models.base import ModelBase


class Peer(ModelBase):
    def __init__(self, address):
        self._address = address

    def get_address(self):
        return self._address

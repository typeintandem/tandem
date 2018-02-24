from tandem.shared.models.base import ModelBase


class Peer(ModelBase):
    def __init__(self, id, public_address, private_address=None):
        self._id = id
        self._public_address = public_address
        self._private_address = private_address

    def __eq__(self, other):
        return (
            self._id == other._id and
            self._public_address == other._public_address and
            self._private_address == other._private_address
        )

    def get_id(self):
        return self._id

    def get_addresses(self):
        addresses = [self._public_address]
        if self._private_address is not None:
            addresses.append(self._private_address)
        return addresses

    def get_public_address(self):
        return self._public_address

    def get_private_address(self):
        return self._private_address

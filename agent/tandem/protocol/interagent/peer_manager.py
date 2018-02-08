import tandem.protocol.interagent.messages as im


class PeerManager:
    def __init__(self, gateway):
        self._peers = {}
        self._gateway = gateway

    def register_peer(self, address):
        # This is temporary. A peer will have a more complex state
        # later on to track the progress of connection set up
        self._peers[address] = True

    def remove_peer(self, address):
        del self._peers[address]

    def broadcast(self, message):
        for address, _ in self._peers.items():
            self._gateway.write_binary_data(im.serialize(message), address)

    def connect_to(self, host, port):
        address = (host, port)
        self._gateway.write_binary_data(im.serialize(im.Hello()), address)
        self.register_peer(address)

    def stop(self):
        self.broadcast(im.Bye())

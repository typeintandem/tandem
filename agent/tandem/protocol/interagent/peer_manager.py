class PeerManager:
    def __init__(self, gateway):
        self._peers = {}
        self._gateway = gateway

    def register_peer(self, address):
        # This is temporary. A peer will have a more complex state
        # later on to track the progress of connection set up
        self._peers[address] = True

    def broadcast(self, message):
        pass

    def connect_to(self, address):
        pass

    def stop(self):
        pass

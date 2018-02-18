import uuid
import socket
import json
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    ConnectRequest,
    NewSession,
    SessionCreated,
)


def recv_data(sock):
    print("Waiting to receive data")
    data, address = sock.recvfrom(4096)
    print("Received data: {} from address: {}".format(data, address))
    return data, address


def send_data(sock, data, address):
    print("Sending data: {} to address: {}".format(data, address))
    sock.sendto(data.encode("utf-8"), address)


def test_create_and_join_existing_session(sock, server_address, self_address):
    host_id = uuid.uuid4()
    send_data(sock, RendezvousProtocolUtils.serialize(NewSession(
        host_id=str(host_id),
        private_address=self_address,
    )), server_address)

    data, address = recv_data(sock)
    message = RendezvousProtocolUtils.deserialize(data)

    if type(message) is not SessionCreated:
        print("Received unexpected message.")
        return

    session_id = uuid.UUID(message.session_id)
    peer_address = (socket.gethostbyname("localhost"), 60002)
    peer_id = uuid.uuid4()
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind(peer_address)

    send_data(sock2, RendezvousProtocolUtils.serialize(ConnectRequest(
        my_id=str(peer_id),
        session_id=str(session_id),
        private_address=peer_address,
    )), server_address)

    print("--- Host Received:")
    recv_data(sock)

    print("--- Joiner Received:")
    recv_data(sock2)
    sock2.close()


def test_invalid_id(sock, server_address, self_address):
    print("")
    print("=== Test Invalid ID ===")
    send_data(sock, RendezvousProtocolUtils.serialize(NewSession(
        host_id="123",
        private_address=self_address,
    )), server_address)
    recv_data(sock)


def main():
    self_address = (socket.gethostbyname("localhost"), 60001)
    server_address = (socket.gethostbyname("localhost"), 60000)

    print("Listening on {}".format(self_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(self_address)

    print("Connecting to rendezvous server")
    test_create_and_join_existing_session(sock, server_address, self_address)
    test_invalid_id(sock, server_address, self_address)


if __name__ == "__main__":
    main()

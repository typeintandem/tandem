import uuid
import socket
import json
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    ConnectRequest,
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
    print("===== Test Creation and Join =====")
    peer1_id = uuid.uuid4()
    session_id = uuid.uuid4()

    send_data(sock, RendezvousProtocolUtils.serialize(ConnectRequest(
        session_id=str(session_id),
        my_id=str(peer1_id),
        private_address=self_address,
    )), server_address)

    peer2_address = (socket.gethostbyname("localhost"), 60002)
    peer2_id = uuid.uuid4()
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind(peer2_address)

    send_data(sock2, RendezvousProtocolUtils.serialize(ConnectRequest(
        my_id=str(peer2_id),
        session_id=str(session_id),
        private_address=peer2_address,
    )), server_address)

    print("--- Peer 1 Received:")
    recv_data(sock)

    print("--- Peer 2 Received:")
    recv_data(sock2)
    sock2.close()


def test_invalid_id(sock, server_address, self_address):
    print("===== Test Invalid ID =====")
    send_data(sock, RendezvousProtocolUtils.serialize(ConnectRequest(
        session_id="123",
        my_id="123",
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

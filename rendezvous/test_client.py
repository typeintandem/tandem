import socket
import json
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    ConnectRequest
)


def recv_data(sock):
    print("Waiting to receive data")
    data, address = sock.recvfrom(4096)
    print("Received data: {} from address: {}".format(data, address))
    return json.loads(data), address


def send_data(sock, data, address):
    print("Sending data: {} to address: {}".format(data, address))
    sock.sendto(data.encode('utf-8'), address)


def main():
    self_address = ('localhost', 60001)
    server_address = ('localhost', 60000)

    print("Listening on {}".format(self_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(self_address)

    print("Connecting to rendezvous server")
    send_data(sock, RendezvousProtocolUtils.serialize(ConnectRequest(
        uuid='1',
        private_address=self_address
    )), server_address)

    while(True):
        data, address = recv_data(sock)


main()

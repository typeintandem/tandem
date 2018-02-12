import argparse
import socket
import json
import time


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_host", default="127.0.0.1")
    parser.add_argument("--target_port", default=60000, type=int)
    parser.add_argument("--self_port", default=60001, type=int)
    return parser.parse_args()


def recv_data(sock):
    print("Waiting to receive data")
    data, address = sock.recvfrom(4096)
    print("Received data: {} from address: {}".format(data, address))
    return json.loads(data), address


def send_data(sock, data, address):
    print("Sending data: {} to address: {}".format(data, address))
    sock.sendto(json.dumps(data), address)


def connect_to(sock, data):
    print("Sending ping to addresses: {}".format(data))
    send_data(sock, create_ping(data[1]), tuple(data[0]))
    send_data(sock, create_ping(data[1]), tuple(data[1]))


def create_ping(address):
    return {
        'type': 'ping',
        'address': address,
    }


def create_pingback(ping):
    return {
        'type': 'pingback',
        'address': ping['address'],
    }


def main():
    args = get_args()
    self_address = (socket.gethostbyname(socket.gethostname()), args.self_port)
    server_address = (args.target_host, args.target_port)

    print("Listening on {}".format(self_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(self_address)

    print("Connecting to rendezvous server")
    send_data(sock, self_address, server_address)

    while(True):
        data, address = recv_data(sock)

        if (type(data) is list and type(data[0]) is list):
            connect_to(sock, data)
        else:
            if data['type'] == 'ping':
                time.sleep(1)
                send_data(sock, create_pingback(data), address)


main()

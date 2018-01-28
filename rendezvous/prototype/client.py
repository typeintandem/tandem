import argparse
import socket
import json

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
    send_data(sock, 'ping!', tuple(data[0]))
    send_data(sock, 'ping!', tuple(data[1]))

def main():
    args = get_args()
    self_address = (socket.gethostbyname(socket.gethostname()), args.self_port)
    server_address = (args.target_host, args.target_port)
    connected_clients = []

    print("Listening on {}".format(self_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(self_address)

    print("Connecting to rendezvous server")
    send_data(sock, self_address, server_address)

    while(True):
        data, address = recv_data(sock)

        if (type(data[0]) is list):
            connect_to(sock, data)
        else:
            print("Just got pinged by {}".format(address))

main()

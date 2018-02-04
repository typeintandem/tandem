import argparse
import socket
import json
import time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self_port", default=60000, type=int)
    return parser.parse_args()

def recv_data(sock):
    print("Waiting to receive data")
    data, address = sock.recvfrom(4096)
    print("Received data: {} from address: {}".format(data, address))
    return json.loads(data), address

def send_data(sock, data, address):
    print("Sending data: {} to address: {}".format(data, address))
    sock.sendto(json.dumps(data), address)

def main():
    args = get_args()
    self_address = (socket.gethostbyname(socket.gethostname()), args.self_port)
    connected_clients = []

    print("Listening on {}".format(self_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(self_address)

    while(True):
        new_data, new_address = recv_data(sock)

        # Send new client information about the connected_clients
        for connected_data, connected_address in connected_clients:
            send_data(sock, (connected_data, connected_address), new_address)
            time.sleep(3)

        time.sleep(3)

        # Send connected_clients information about the new client
        for connected_data, connected_address in connected_clients:
            send_data(sock, (new_data, new_address), connected_address)

        connected_clients.append((new_data, new_address))

main()

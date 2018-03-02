import os
import socket

PROJECT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    '..',
)
BASE_DIR = os.path.dirname(PROJECT_ROOT)
CRDT_PATH = os.path.join(BASE_DIR, "..", "crdt")
PLUGIN_PATH = os.path.join(BASE_DIR, "..", "plugins")
# RENDEZVOUS_ADDRESS = (socket.gethostbyname("ec2-52-15-238-77.us-east-2.compute.amazonaws.com"), 60000)
RENDEZVOUS_ADDRESS = (socket.gethostbyname("localhost"), 60000)

import os
import socket

# Tandem will try to establish a direct connection with other peers in a
# session. However, this is not always possible. When Tandem is unable to
# establish a peer-to-peer connection, we will relay messages to each peer
# through our servers. If this is undesirable for your use case, you can set
# this flag to "False".
#
# Please note that with relay disabled, you will not be able to collaborate
# with any peers that Tandem cannot reach directly. Tandem does not notify you
# if a peer-to-peer connection cannot be established.
USE_RELAY = True

# DO NOT edit anything below this unless you know what you're doing!

PROJECT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    '..',
)
BASE_DIR = os.path.dirname(PROJECT_ROOT)
CRDT_PATH = os.path.join(BASE_DIR, "..", "crdt")
PLUGIN_PATH = os.path.join(BASE_DIR, "..", "plugins")
RENDEZVOUS_ADDRESS = (
    socket.gethostbyname("rendezvous.typeintandem.com"),
    60000,
)

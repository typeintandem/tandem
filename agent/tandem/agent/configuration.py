import os

PROJECT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    '..',
)
BASE_DIR = os.path.dirname(PROJECT_ROOT)
CRDT_PATH = os.path.join(BASE_DIR, "..", "crdt")
PLUGIN_PATH = os.path.join(BASE_DIR, "..", "plugins")

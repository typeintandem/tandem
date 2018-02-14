import json
import os
from subprocess import Popen, PIPE
from tandem.agent.configuration import CRDT_PATH

CRDT_PROCESS = ["node", os.path.join(CRDT_PATH, "build", "bundle.js")]


class Document:
    def __init__(self):
        self._crdt_process = None
        self._pending_remote_operations = []
        self._write_request_sent = False

    def start(self):
        self._crdt_process = Popen(
            CRDT_PROCESS,
            stdin=PIPE,
            stdout=PIPE,
            encoding="utf-8",
        )

    def stop(self):
        self._crdt_process.stdin.close()
        self._crdt_process.terminate()
        self._crdt_process.wait()

    def apply_operations(self, operations_list):
        return self._call_remote_function(
            "applyOperations",
            [operations_list],
        )

    def get_document_text(self):
        return self._call_remote_function("getDocumentText")

    def set_text_in_range(self, start, end, text):
        return self._call_remote_function(
            "setTextInRange",
            [start, end, text],
        )

    def get_document_operations(self):
        return self._call_remote_function("getDocumentOperations")

    def enqueue_remote_operations(self, operations_list):
        self._pending_remote_operations.extend(operations_list)

    def apply_queued_operations(self):
        text_patches = self.apply_operations(self._pending_remote_operations)
        self._pending_remote_operations.clear()
        return text_patches

    def write_request_sent(self):
        return self._write_request_sent

    def set_write_request_sent(self, value):
        self._write_request_sent = value

    def _call_remote_function(self, function_name, parameters=None):
        call_message = {"function": function_name}
        if parameters is not None:
            call_message["parameters"] = parameters
        self._crdt_process.stdin.write(json.dumps(call_message))
        self._crdt_process.stdin.write("\n")
        self._crdt_process.stdin.flush()

        response = json.loads(self._crdt_process.stdout.readline())
        return response["value"]

import json
from subprocess import Popen, PIPE

CRDT_PROCESS = ["node", "../crdt/build/bundle.js"]


class Document:
    def __init__(self):
        self._crdt_process = None

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

    def _call_remote_function(self, function_name, parameters=None):
        call_message = {"function": function_name}
        if parameters is not None:
            call_message["parameters"] = parameters
        self._crdt_process.stdin.write(json.dumps(call_message))
        self._crdt_process.stdin.write("\n")
        self._crdt_process.stdin.flush()

        response = json.loads(self._crdt_process.stdout.readline())
        return response["value"]

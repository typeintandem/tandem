import os
import sys
import random

from subprocess import Popen, PIPE
from threading import Thread

import sublime
import sublime_plugin

from tandem.diff_match_patch import diff_match_patch
from tandem.edit import Edit

# sys hack to add enum, required by the messages module file
sys.path.append(os.path.join(os.path.dirname(__file__), "enum-dist"))
import tandem.agent.tandem.protocol.editor.messages as m  # noqa


DEBUG = True
is_active = False
is_processing = False
patch = diff_match_patch()


def spawn_agent(extra_args=None):
    if extra_args is None:
        extra_args = []
    dirname = os.path.dirname(__file__)
    filename = str(os.path.join(dirname, "agent/main.py"))
    return Popen(
        ["python3", filename] + extra_args,
        stdin=PIPE,
        stdout=PIPE,
    )


def get_string_port():
    starting_port = random.randint(60600, 62600)
    return str(starting_port)


def index_to_point(buffer, index):
    index_left = index
    for i in range(len(buffer)):
        if index_left >= len(buffer[i]) + 1:
            index_left -= len(buffer[i])
            index_left -= 1
        else:
            return (i, index_left)


def error():
    print("An error occurred.")


class TandemCommand(sublime_plugin.TextCommand):
    def run(self, edit, host_ip=None, host_port=None):
        global tandem_agent
        tandem_agent.start(self.view, host_ip, host_port)


class TandemStopCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global tandem_agent
        tandem_agent.stop()


class TandemPlugin:

    def _current_buffer(self):
        return self._view.substr(sublime.Region(0, self._view.size()))

    def _initialize(self, view):
        self._view = view
        self._buffer = self._current_buffer()

        self._output_checker = Thread(target=self._check_message)

        self._connect_to = None

    def _start_agent(self):
        self._agent_port = get_string_port()
        self._agent = spawn_agent([
            "--port",
            self._agent_port,
            "--log-file",
            "/tmp/tandem-agent-{}.log".format(self._agent_port),
        ])

        if self._connect_to is not None:
            host_ip, host_port = self._connect_to
            message = m.ConnectTo(host_ip, int(host_port))
            self._agent.stdin.write(m.serialize(message).encode("utf-8"))
            self._agent.stdin.write("\n".encode("utf-8"))
            self._agent.stdin.flush()

        print("Bound agent to port: {}".format(self._agent_port))

        self._output_checker.start()

    def _shut_down_agent(self):
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self):
        current_buffer = self._current_buffer()

        if len(current_buffer) != len(self._buffer):
            self._send_patches(current_buffer)
        else:
            for i in range(len(current_buffer)):
                if current_buffer[i] != self._buffer[i]:
                    self._send_patches(current_buffer)
                    break

        self._buffer = current_buffer

    def _create_patch(self, start, end, text):
        if start is None or end is None or text is None:
            # Raise an error if in debug mode, otherwise return None
            if DEBUG:
                raise ValueError
            else:
                return None
        return [
            {
                "start": {
                    "row": start[0],
                    "column": start[1],
                },
                "end": {
                    "row": end[0],
                    "column": end[1],
                },
                "text": "",
            },
            {
                "start": {
                    "row": start[0],
                    "column": start[1],
                },
                "end": {
                    "row": 0,
                    "column": 0,
                },
                "text": text,
            }
        ]

    def _send_patches(self, current_buffer):
        try:
            prev_contents = self._buffer
            curr_contents = current_buffer
            diff_patches = patch.patch_make(prev_contents, curr_contents)

            patches = []
            for p in diff_patches:
                start_index = p.start1
                end_index = p.start1 + p.length1

                start_rc = index_to_point(
                    prev_contents.split(os.linesep),
                    start_index,
                )
                end_rc = index_to_point(
                    prev_contents.split(os.linesep),
                    end_index,
                )

                text = []
                for (op, data) in p.diffs:
                    if op == diff_match_patch.DIFF_INSERT or \
                            op == diff_match_patch.DIFF_EQUAL:
                        text.append(data)
                text = "".join(text)

                patches.extend(
                  self._create_patch(start_rc, end_rc, text)
                )

            patches = [p for p in patches if p is not None]
            if len(patches) > 0:
                message = m.NewPatches(patches)
                self._agent.stdin.write(m.serialize(message).encode("utf-8"))
                self._agent.stdin.write("\n".encode("utf-8"))
                self._agent.stdin.flush()
        except:
            error()
            if DEBUG:
                raise

    def _check_message(self):
        for line in iter(self._agent.stdout.readline, b""):
            def callback():
                self._handle_message(line)
            sublime.set_timeout(callback, 0)

    def _handle_write_request(self, message):
        # Don't allow any more buffer modifications
        self._view.set_read_only(True)

        # Flush out any non-diff'd changes first
        self.check_buffer()

        # Allow agent to apply remote operations
        ack = m.WriteRequestAck(message.seq)
        self._agent.stdin.write(m.serialize(ack).encode("utf-8"))
        self._agent.stdin.write("\n".encode("utf-8"))
        self._agent.stdin.flush()

    def _handle_apply_text(self, message):
        text = os.linesep.join(message.contents)
        with Edit(self._view) as edit:
            edit.replace(
                sublime.Region(0, self._view.size()),
                text,
            )
        self._buffer = self._current_buffer()

    def _handle_apply_patches(self, message):
        if not self._view.is_read_only():
            raise ValueError("Buffer should be read-only when"
                             "applying patches.")
        self._view.set_read_only(False)

        for patch in message.patch_list:
            start = patch["oldStart"]
            end = patch["oldEnd"]
            text = patch["newText"]
            start_point = self._view.text_point(
                start["row"],
                start["column"],
            )
            end_point = self._view.text_point(
                end["row"],
                end["column"],
            )
            """
            Edit cannot be passed around
            https://forum.sublimetext.com/t/multithreaded-plugin/14439
            Use view abstraction instead.
            """
            with Edit(self._view) as edit:
                edit.replace(
                    sublime.Region(start_point, end_point),
                    text,
                )

        self._buffer = self._current_buffer()

    def _handle_message(self, msg):
        message = m.deserialize(msg.decode("utf-8"))
        global is_processing
        is_processing = True

        if isinstance(message, m.ApplyText):
            self._handle_apply_text(message)
        elif isinstance(message, m.WriteRequest):
            self._handle_write_request(message)
        elif isinstance(message, m.ApplyPatches):
            self._handle_apply_patches(message)

        is_processing = False

    def start(self, view, host_ip=None, host_port=None):
        global is_active
        if is_active:
            print("Cannot start. An instance is already running on :{}".format(
                self._agent_port,
            ))
            return

        if host_ip is not None and host_port is None:
            print(
                "Cannot start. IP specified. You must also provide a port",
            )
            return

        self._initialize(view)

        if host_ip is not None:
            self._connect_to = (host_ip, host_port)

        self._start_agent()
        is_active = True

    def stop(self):
        global is_active
        if not is_active:
            print("No Tandem instance running.")
            return

        is_active = False

        self._shut_down_agent()

        if self._output_checker.isAlive():
            self._output_checker.join()


class TandemTextChangedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        global is_active
        global is_processing
        if not is_active or is_processing:
            return

        global tandem_agent
        tandem_agent.check_buffer()


tandem_agent = TandemPlugin()

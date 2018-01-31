import os
import sys
import random

from subprocess import Popen, PIPE
from threading import Thread, Event

import sublime
import sublime_plugin

from tandem.diff_match_patch import diff_match_patch
from tandem.edit import Edit

# sys hack to add enum, required by the messages module file
sys.path.append(os.path.join(os.path.dirname(__file__), "enum-dist"))
import tandem.agent.tandem.protocol.editor.messages as m  # noqa


DEBUG = False
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


def index_to_point(buffer_line_lengths, index):
    index_left = index
    for i in range(len(buffer_line_lengths)):
        if index_left >= buffer_line_lengths[i] + 1:
            index_left -= buffer_line_lengths[i] + 1
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
        self._text_applied = Event()

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
        self._agent_stdout_iter = iter(self._agent.stdout.readline, b"")

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
            length_buffer = [len(x) for x in prev_contents.split(os.linesep)]

            for p in diff_patches:
                start_index = p.start1
                end_index = p.start1 + p.length1

                start_index_offset = 0
                end_index_offset = 0

                while(len(p.diffs)):
                    (op, data) = p.diffs[0]
                    if (op != diff_match_patch.DIFF_EQUAL):
                        break
                    start_index_offset = start_index_offset + len(data)
                    p.diffs.pop(0)

                while(len(p.diffs)):
                    (op, data) = p.diffs[-1]
                    if (op != diff_match_patch.DIFF_EQUAL):
                        break
                    end_index_offset = end_index_offset + len(data)
                    p.diffs.pop()

                start_rc = index_to_point(
                    length_buffer,
                    start_index + start_index_offset,
                )
                end_rc = index_to_point(
                    length_buffer,
                    end_index - end_index_offset,
                )

                text = []

                for (op, data) in p.diffs:
                    if op == diff_match_patch.DIFF_INSERT or \
                            op == diff_match_patch.DIFF_EQUAL:
                        text.append(data)

                text = "".join(text)

                text_lengths = [len(word) for word in text.split(os.linesep)]

                if start_rc[0] == end_rc[0]:
                    length_buffer[start_rc[0]] += text_lengths[0]
                    length_buffer[start_rc[0]] -= end_rc[1] - start_rc[1]
                    length_buffer[start_rc[0] + 1 : start_rc[0] + 1] = text_lengths[1:]
                else:
                    if len(text_lengths) > 1:
                        length_buffer[start_rc[0]] = start_rc[1] + text_lengths[0]
                        length_buffer[end_rc[0]] = length_buffer[end_rc[0]] \
                            - end_rc[1] + text_lengths[-1]
                        length_buffer[start_rc[0] + 1 : end_rc[0]] = text_lengths[1:-1]
                    else:
                        length_buffer[start_rc[0]] = start_rc[1] + text_lengths[0] + length_buffer[end_rc[0]] - end_rc[1]
                        length_buffer[start_rc[0] + 1 : end_rc[0] + 1] = []

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

    def _read_message(self):
        try:
            binary_line = next(self._agent_stdout_iter)
            line = binary_line.decode("utf-8")
            return m.deserialize(line)
        except StopIteration:
            return None

    def _check_message(self):
        while True:
            self._text_applied.clear()

            message = self._read_message()
            if message is None:
                break

            def callback():
                self._handle_message(message)
            sublime.set_timeout(callback, 0)

            self._text_applied.wait()

    def _handle_write_request(self, message):
        # Flush out any non-diff'd changes first
        self.check_buffer()

        # Allow agent to apply remote operations
        ack = m.WriteRequestAck(message.seq)
        self._agent.stdin.write(m.serialize(ack).encode("utf-8"))
        self._agent.stdin.write("\n".encode("utf-8"))
        self._agent.stdin.flush()

        try:
            # Read, expect, and process an ApplyPatches message
            message = self._read_message()
            if not isinstance(message, m.ApplyPatches):
                raise ValueError("Invalid message. Expected ApplyPatches.")
            self._handle_apply_patches(message)
        except ValueError as v:
            raise v

    def _handle_apply_patches(self, message):
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

    def _handle_message(self, message):
        global is_processing
        is_processing = True

        try:
            if isinstance(message, m.WriteRequest):
                self._handle_write_request(message)
            elif isinstance(message, m.ApplyPatches):
                raise ValueError("Invalid message. ApplyPatches must be "
                                 "preceeded by a WriteRequest.")
            else:
                raise ValueError("Unsupported message.")
        except ValueError as v:
            raise v
        finally:
            is_processing = False
            self._text_applied.set()

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

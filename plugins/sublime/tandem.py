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
import tandem.agent.tandem.agent.protocol.messages.editor as m  # noqa


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


def show_message(msg, show_gui):
    if show_gui:
        sublime.message_dialog(msg)
    else:
        print(msg)


class TandemCommand(sublime_plugin.TextCommand):
    def run(self, edit, host_ip=None, host_port=None, show_gui=False):
        global tandem_agent
        tandem_agent.start(self.view, show_gui=show_gui)

    def is_enabled(self):
        global is_active
        return not is_active


class TandemConnectCommand(sublime_plugin.TextCommand):
    def _start(self, args):
        global tandem_agent
        tandem_agent.start(self.view, session_id=args, show_gui=True)

    def run(self, edit):
        global is_active
        if is_active:
            msg = "Cannot start. An instance is already running on :{}".format(
                tandem_agent.agent_port,
            )
            show_message(msg, True)
            return
        sublime.active_window().show_input_panel(
            caption="Enter Session ID",
            initial_text="",
            on_done=self._start,
            on_change=None,
            on_cancel=None,
        )

    def is_enabled(self):
        global is_active
        return not is_active


class TandemStopCommand(sublime_plugin.TextCommand):
    def run(self, edit, show_gui=False):
        global tandem_agent
        tandem_agent.stop(show_gui)

    def is_enabled(self):
        global is_active
        return is_active


class TandemSessionCommand(sublime_plugin.TextCommand):
    def run(self, edit, show_gui=False):
        global tandem_agent
        tandem_agent.show_session_id(show_gui)

    def is_enabled(self):
        global is_active
        return is_active



class TandemPlugin:

    @property
    def agent_port(self):
        return self._agent_port

    @property
    def _current_buffer(self):
        return self._view.substr(sublime.Region(0, self._view.size()))

    def _initialize(self, view):
        self._view = view
        self._buffer = ""

        self._output_checker = Thread(target=self._check_message)

        self._text_applied = Event()
        self._session_id = None

    def _start_agent(self):
        self._agent_port = get_string_port()
        self._agent = spawn_agent([
            "--port",
            self._agent_port,
            "--log-file",
            "/tmp/tandem-agent-{}.log".format(self._agent_port),
        ])

        if self._connect_to is not None:
            message = m.JoinSession(self._connect_to)
        else:
            message = m.HostSession()
        self._agent.stdin.write(m.serialize(message).encode("utf-8"))
        self._agent.stdin.write("\n".encode("utf-8"))
        self._agent.stdin.flush()

        self._agent_stdout_iter = iter(self._agent.stdout.readline, b"")

        self._output_checker.start()

    def _shut_down_agent(self):
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self, buffer_id):
        if self._view.buffer_id() != buffer_id:
            return

        current_buffer = self._current_buffer

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
                    length_buffer[start_rc[0] + 1: start_rc[0] + 1] = \
                        text_lengths[1:]
                else:
                    if len(text_lengths) > 1:
                        length_buffer[start_rc[0]] = \
                            start_rc[1] + text_lengths[0]
                        length_buffer[end_rc[0]] = length_buffer[end_rc[0]] \
                            - end_rc[1] + text_lengths[-1]
                        length_buffer[start_rc[0] + 1: end_rc[0]] = \
                            text_lengths[1:-1]
                    else:
                        length_buffer[start_rc[0]] = \
                            start_rc[1] + text_lengths[0] \
                            + length_buffer[end_rc[0]] - end_rc[1]
                        length_buffer[start_rc[0] + 1: end_rc[0] + 1] = []

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
        self.check_buffer(self._view.buffer_id())

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

        self._buffer = self._current_buffer

    def _handle_message(self, message):
        global is_processing
        is_processing = True

        try:
            if isinstance(message, m.WriteRequest):
                self._handle_write_request(message)
            elif isinstance(message, m.ApplyPatches):
                raise ValueError("Invalid message. ApplyPatches must be "
                                 "preceeded by a WriteRequest.")
            elif isinstance(message, m.SessionInfo):
                self._session_id = message.session_id
                show_message("Session ID: {}".format(message.session_id), True)
            else:
                raise ValueError("Unsupported message.")
        except ValueError as v:
            raise v
        finally:
            is_processing = False
            self._text_applied.set()

    def start(self, view, session_id=None, show_gui=False):
        global is_active
        if is_active:
            msg = "Cannot start. An instance is already running on :{}".format(
                self._agent_port,
            )
            show_message(msg, show_gui)
            return

        self._connect_to = session_id

        if self._connect_to is not None:
            view = sublime.active_window().new_file()

        self._initialize(view)

        self._start_agent()
        is_active = True

        if self._connect_to is None:
            self.check_buffer(view.buffer_id())

    def stop(self, show_gui):
        global is_active
        if not is_active:
            msg = "No Tandem instance running."
            show_message(msg, show_gui)
            return

        is_active = False

        self._shut_down_agent()

        if self._output_checker.isAlive():
            self._output_checker.join()

        msg = "Tandem instance shut down."
        show_message(msg, show_gui)

    def show_session_id(self, show_gui):
        global is_active
        if not is_active:
            msg = "No Tandem instance running."
            show_message(msg, show_gui)
            return

        if self._session_id is not None:
            message = "Session ID: {}".format(self._session_id)
        else:
            message = "Error: No Session ID assigned."

        show_message(message, show_gui)


class TandemTextChangedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        global is_active
        global is_processing
        if not is_active or is_processing:
            return

        global tandem_agent
        tandem_agent.check_buffer(view.buffer_id())


tandem_agent = TandemPlugin()

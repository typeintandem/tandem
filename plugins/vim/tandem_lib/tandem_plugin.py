import os
import sys
import random
from time import sleep

from subprocess import Popen, PIPE
from threading import Thread, Event

from diff_match_patch import diff_match_patch
import agent.tandem.protocol.editor.messages as m
from agent.tandem.configuration import BASE_DIR

DEBUG = True
is_active = False
patch = diff_match_patch()


def spawn_agent(extra_args=None):
    if extra_args is None:
        extra_args = []
    return Popen(
        ["python3", os.path.join(BASE_DIR, "main.py")] + extra_args,
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
    print "An error occurred."
    global DEBUG
    if DEBUG:
        raise


class TandemPlugin(object):
    def __init__(self, vim, on_start, message_handler):
        self._vim = vim
        self._on_start = on_start
        self._message_handler = message_handler

    def _initialize(self):
        self._buffer = ['']

        if self._connect_to is not None:
            self._vim.command('enew')

        self._output_checker = Thread(target=self._agent_listener)

        self._text_applied = Event()

    def _start_agent(self):
        self._agent_port = get_string_port()
        self._agent = spawn_agent([
            "--port",
            self._agent_port,
            "--log-file",
            "/tmp/tandem-agent-{}.log".format(self._agent_port),
        ])
        self._agent_stdout_iter = iter(self._agent.stdout.readline, b"")

        if self._connect_to is not None:
            host_ip, host_port = self._connect_to
            message = m.ConnectTo(host_ip, int(host_port))
            self._agent.stdin.write(m.serialize(message))
            self._agent.stdin.write("\n")
            self._agent.stdin.flush()

        self._output_checker.start()

        self._vim.command('echom "Bound agent to port: {}"'.format(self._agent_port))

    def _check_document_sync(self):
        global is_active
        while is_active:
            with self._read_write_check:
                if not is_active:
                    break

                current_buffer = self._vim.current.buffer[:]
                message = m.CheckDocumentSync(current_buffer)

                self._agent.stdin.write(m.serialize(message))
                self._agent.stdin.write("\n")
                self._agent.stdin.flush()

            sleep(0.5)

    def _shut_down_agent(self):
        self._agent_stdout_iter = None
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self):
        global is_active
        if not is_active:
          return

        current_buffer = self._vim.current.buffer[:]

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
                raise ValueError("Start, end, or text is None!")
            else:
                return None

        result = []

        if not (start[0] == end[0] and start[1] == end[1]):
            result.append({
                "start": {"row": start[0], "column": start[1]},
                "end": {"row": end[0], "column": end[1]},
                "text": "",
            })

        if text:
            result.append({
                "start": {"row": start[0], "column": start[1]},
                "end": {"row": 0, "column": 0},
                "text": text,
            })

        return result

    def _send_patches(self, current_buffer):
        try :
            prev_contents = os.linesep.join(self._buffer)
            curr_contents = os.linesep.join(current_buffer)
            diff_patches = patch.patch_make(prev_contents, curr_contents)

            patches = []
            length_buffer = [len(x) for x in self._buffer]

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

                start_rc = index_to_point(length_buffer, start_index + start_index_offset)
                end_rc = index_to_point(length_buffer, end_index - end_index_offset)

                text = []

                for (op, data) in p.diffs:
                    if op == diff_match_patch.DIFF_INSERT or op == diff_match_patch.DIFF_EQUAL:
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
                        length_buffer[end_rc[0]] = length_buffer[end_rc[0]] - end_rc[1] + text_lengths[-1]
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
                self._agent.stdin.write(m.serialize(message))

                self._agent.stdin.write("\n")
                self._agent.stdin.flush()
        except:
            error()

    def _agent_listener(self):
        while True:
            message = self._read_message()
            if message is None:
                break
            self._handle_message(message)

    def _read_message(self):
        try:
            binary_line = self._agent_stdout_iter.next()
            line = binary_line.decode("utf-8")
            return m.deserialize(line)
        except StopIteration:
            return None

    def handle_apply_text(self, message):
        self._vim.current.buffer[:] = message.contents
        # TODO: Send ack back to agent.
        self._buffer = self._vim.current.buffer[:]
        self._vim.command(":redraw")

    def handle_write_request(self, message):
        # Flush out any non-diff'd changes first
        self.check_buffer()

        # Allow agent to apply remote operations
        self._agent.stdin.write(m.serialize(m.WriteRequestAck(message.seq)))
        self._agent.stdin.write("\n")
        self._agent.stdin.flush()

        # Apply results of the remote operations
        apply_patches_message = self._read_message()
        if not isinstance(apply_patches_message, m.ApplyPatches):
            raise ValueError("Invalid protocol message!")
        self._handle_apply_patches(apply_patches_message)

    def _handle_apply_patches(self, message):
        for patch in message.patch_list:
            start = patch["oldStart"]
            end = patch["oldEnd"]
            text = patch["newText"]

            current_buffer = self._vim.current.buffer[:]

            before_in_new_line = current_buffer[start["row"]][:start["column"]]
            after_in_new_line = current_buffer[end["row"]][end["column"]:]

            new_lines = text.split(os.linesep)
            if len(new_lines) > 0:
                new_lines[0] = before_in_new_line + new_lines[0]
            else:
                new_lines = [before_in_new_line]

            new_lines[-1] = new_lines[-1] + after_in_new_line

            self._vim.current.buffer[start["row"] : end["row"] + 1] = new_lines

        self._buffer = self._vim.current.buffer[:]
        self._vim.command(":redraw")

    def _handle_message(self, message):
        self._message_handler(message)

    def start(self, host_ip=None, host_port=None):
        global is_active
        if is_active:
            print "Cannot start. An instance is already running on :{}".format(self._agent_port)
            return

        if host_ip is not None and host_port is None:
            print "Cannot start. IP specified. You must also provide a port"
            return

        self._connect_to = (host_ip, host_port) if host_ip is not None else None

        self._initialize()

        self._start_agent()
        is_active = True

        self._on_start()

        if self._connect_to is None:
            self.check_buffer()

    def stop(self, invoked_from_autocmd=True):
        global is_active
        if not is_active:
            if not invoked_from_autocmd:
                print "No instance running."
            return

        is_active = False

        self._shut_down_agent()

        if self._output_checker.isAlive():
            self._output_checker.join()

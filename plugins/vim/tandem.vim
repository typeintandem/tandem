if !has('python')
  " :echom is persistent messaging. See
  " http://learnvimscriptthehardway.stevelosh.com/chapters/01.html
  :echom 'ERROR: Please use a version of Vim with Python support'
  finish
endif

if !executable('python3')
  :echom 'ERROR: Global python3 install required.'
  finish
endif

" Bind the Tandem function to a globally available command
" e.g. :Tandem h
" e.g. :Tandem <anythingelse> localhost 1234
com! -nargs=* Tandem py tandem_agent.start(<f-args>)

com! TandemStop py tandem_agent.stop(False)

python << EOF

import os
import sys
import random
from time import sleep
import pprint

from subprocess import Popen, PIPE
from threading import Lock, Thread, Semaphore

import vim

# For now, add the tandem agent path to the system path so that we can use the
# existing messages protocol implementation
tandem_agent_path = os.path.abspath('../../agent')
if tandem_agent_path not in sys.path:
    sys.path.insert(0, tandem_agent_path)
local_path = os.path.abspath('./')
if local_path not in sys.path:
    sys.path.insert(0, local_path)

from diff_match_patch import diff_match_patch
import tandem.protocol.editor.messages as m

DEBUG = False
is_active = False
count = 0
pp = pprint.PrettyPrinter(indent=4)
patch = diff_match_patch()

def spawn_agent(extra_args=None):
    if extra_args is None:
        extra_args = []
    return Popen(
        ["python3", "../../agent/main.py"] + extra_args,
        stdin=PIPE,
        stdout=PIPE,
    )


def get_string_port():
    starting_port = random.randint(60600, 62600)
    return str(starting_port)


class TandemPlugin:

    def __init__(self):
        self._buffer = vim.current.buffer[:]

        self._input_checker = Thread(target=self._check_buffer)
        self._output_checker = Thread(target=self._check_message)
        self._document_syncer = Thread(target=self._check_document_sync)
        self._should_check_buffer = Semaphore(0)
        self._ui = Semaphore(0)
        self._read_write_check = Lock()

    def _start_agent(self):
        self._agent_port = get_string_port()
        self._agent = spawn_agent([
            "--port",
            self._agent_port,
            "--log-file",
            "/tmp/tandem-agent-{}.log".format(self._agent_port),
        ])

        if not self._is_host:
            message = m.ConnectTo(self._host_ip, int(self._host_port))
            self._agent.stdin.write(m.serialize(message))
            self._agent.stdin.write(os.linesep)
            self._agent.stdin.flush()

        print "Bound agent to port: {}".format(self._agent_port)

        self._output_checker.start()

    def _check_document_sync(self):
        global is_active
        while is_active:
            with self._read_write_check:
                if not is_active:
                    break

                continue
                current_buffer = vim.current.buffer[:]
                message = m.CheckDocumentSync(current_buffer)

                self._agent.stdin.write(m.serialize(message))
                self._agent.stdin.write(os.linesep)
                self._agent.stdin.flush()

            sleep(0.5)

    def _shut_down_agent(self):
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self):
        # Allow the user input to be checked.
        self._should_check_buffer.release()
        # Block the UI until the user input is processed.
        self._ui.acquire()

    def _check_buffer(self):
        while True:
            # Wait on a signal from the autocommand that the text has changed
            self._should_check_buffer.acquire()
            global is_active
            if not is_active:
              break

            with self._read_write_check:
                current_buffer = vim.current.buffer[:]

                if len(current_buffer) != len(self._buffer):
                    self._send_patches(current_buffer)
                else:
                    for i in range(len(current_buffer)):
                        if current_buffer[i] != self._buffer[i]:
                            self._send_patches(current_buffer)
                            break

                self._buffer = current_buffer
                # Unblock the UI.
                self._ui.release()

        self._ui.release()

    def _create_patch(self, start, end, text):
        if start is None or end is None or text is None:
            # Raise an error if in debug mode, otherwise return None
            if DEBUG:
                raise ValueError
            else:
                return None
        return {
            "start": {
                "row": start[0],
                "column": start[1],
            },
            "end": {
                "row": end[0],
                "column": end[1],
            },
            "text": text,
        }

    def _send_patches(self, current_buffer):
        try :
            prev_contents = os.linesep.join(self._buffer)
            curr_contents = os.linesep.join(current_buffer)
            diff_patches = patch.patch_make(prev_contents, curr_contents)

            patches = []
            for p in diff_patches:
                start = (None, None)
                end = (None, None)

                start_index = p.start1
                end_index = p.start1 + p.length1

                line = 0
                start_counter = 0

                print "==========="

                for row in self._buffer:
                    if start_counter + len(row) + 1 >= start_index:
                        col = start_index - start_counter
                        print "col: ", col
                        print "sstart_index: ", start_index
                        print "start_counter: ", start_counter
                        if col >= len(self._buffer[line]):
                            next_line = min(line + 1, len(self._buffer) - 1)
                            print "adjusting start due to line length overflow or newline"
                            if next_line == line:
                                print "... to ... sorry, same line"
                                # end = (line, max(0, max(len(self._buffer[line]) - 1, col - 1)))
                                start = (line, col)
                            else:
                                print "...to start of next line"
                                start = (next_line, 0)
                        start = (line, col)
                        break

                    line += 1
                    start_counter += len(row) + 1

                line = 0
                end_counter = 0
                for row in self._buffer:
                    if end_counter + len(row) + 1 >= end_index:
                        print "col: ", col
                        print "end_index: ", end_index
                        print "end_counter: ", end_counter
                        col = end_index - end_counter
                        if col >= len(self._buffer[line]):
                          # or self._buffer[line][col] == os.linesep:
                              # end = (line, max(0, col - 1))
                            print "adjusting end due to line length overflow or newline"
                            next_line = min(line + 1, len(self._buffer) - 1)
                            if next_line == line:
                                print "... to ... sorry, same line"
                                # end = (line, max(0, max(len(self._buffer[line]) - 1, col - 1)))
                                end = (line, col)
                            else:
                                print "...to start of next line"
                                end = (next_line, 0)
                        else:
                            end = (line, col)
                        break

                    line += 1
                    end_counter += len(row) + 1

                text = []
                for (op, data) in p.diffs:
                    if op == diff_match_patch.DIFF_INSERT or op == diff_match_patch.DIFF_EQUAL:
                        text.append(data)
                text = "".join(text)

                print str(p)
                print "start: ", start
                print "end: ", end
                if text == "":
                    print "text: emptystr"
                elif text == os.linesep:
                    print "text: newline"
                else:
                    print "text: ", text

                patches.append(
                  self._create_patch(start, end, text)
                )

            patches = [p for p in patches if p is not None]
            if len(patches) > 0:
                message = m.NewPatches(patches)
                self._agent.stdin.write(m.serialize(message))

                self._agent.stdin.write(os.linesep)
                self._agent.stdin.flush()

                if DEBUG:
                    print "Sent patches: " + str(message.patch_list)
        except:
            raise

    def _check_message(self):
        while True:
            line = self._agent.stdout.readline()
            if line == "":
                break
            self._handle_message(line)

    def _handle_message(self, msg):
        try:
            # Wait until the input checker thread is done.
            message = m.deserialize(msg)
            with self._read_write_check:
                if isinstance(message, m.ApplyText):
                    if DEBUG:
                        print "============="
                        print "Applying text."
                        print str(message.contents)
                    vim.current.buffer[:] = message.contents
                    # TODO: Send ack back to agent.
                elif isinstance(message, m.ApplyPatches):
                    if DEBUG or True:
                        print "============="
                        print "Received patches: "
                        pp.pprint(message.patch_list)
                    for patch in message.patch_list:
                        start = patch["oldStart"]
                        end = patch["oldEnd"]
                        text = patch["newText"]

                        current_buffer = vim.current.buffer[:]
                        print "buffer: ", current_buffer
                        print "curr patch: "
                        pp.pprint(patch)

                        buffer_as_string = os.linesep.join(current_buffer)
                        start_index = 0
                        end_index = 0
                        counter = 0
                        both_done = 0

                        for row in current_buffer:
                            if start["row"] == counter:
                                start_index = start_index + start["column"]
                                both_done = both_done + 1

                            if end["row"] == counter:
                                end_index = end_index + end["column"]
                                both_done = both_done + 1

                            if both_done >= 2:
                                break

                            start_index = start_index + len(row)
                            end_index = end_index + len(row)
                            counter += 1

                        buffer_as_string = buffer_as_string[:start_index] + \
                            text + buffer_as_string[end_index + 1:]

                        extra_line = [''] if text == os.linesep else []
                        print "ex_line: ", extra_line
                        vim.current.buffer[:] = buffer_as_string.splitlines() + extra_line

                self._buffer = vim.current.buffer[:]
                vim.command(":redraw")
        except:
            print "An error occurred."
            if DEBUG or True:
                raise

    def _set_up_autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd TextChanged <buffer> py tandem_agent.check_buffer()')
        vim.command('autocmd TextChangedI <buffer> py tandem_agent.check_buffer()')
        vim.command('autocmd VimLeave * py tandem_agent.stop()')


    def start(self, host_arg, host_ip=None, host_port=None):
        global is_active
        if is_active:
            print "Cannot start. An instance is already running on :{}".format(self._agent_port)
            return

        self._is_host = host_arg == "h"
        if not self._is_host:
            self._host_ip = host_ip
            self._host_port = host_port

        self._start_agent()
        is_active = True

        self._input_checker.start()
        self._document_syncer.start()
        self._set_up_autocommands()


    def stop(self, invoked_from_autocmd=True):
        global is_active
        if not is_active:
            if not invoked_from_autocmd:
                print "No instance running."
            return

        is_active = False
        self._should_check_buffer.release()

        self._shut_down_agent()

        if self._input_checker.isAlive():
            self._input_checker.join()
        if self._output_checker.isAlive():
            self._output_checker.join()


tandem_agent = TandemPlugin()

EOF

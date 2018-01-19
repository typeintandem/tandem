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

" Bind the Tandem functions to globally available commands.
" =================
" Start agent with `:Tandem`
" Start agent and connect to network with `:Tandem <localhost | ip> <port>`
com! -nargs=* Tandem py tandem_agent.start(<f-args>)
" ================
" Stop agent (and disconnect from network) with `:TandemStop`
com! TandemStop py tandem_agent.stop(False)

python << EOF

import os
import sys
import random
from time import sleep

from subprocess import Popen, PIPE
from threading import Lock, Thread, Semaphore, Event

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

DEBUG = True
is_active = False
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


def index_to_point(buffer, index):
    index_left = index
    for i in range(len(buffer)):
        if index_left >= len(buffer[i]) + 1:
            index_left -= len(buffer[i])
            index_left -= 1
        else:
            return (i, index_left)


def error():
    print "An error occurred."
    global DEBUG
    if DEBUG:
        raise


class TandemPlugin:

    def _initialize(self):
        self._buffer = ['']

        if self._connect_to is not None:
            vim.command('enew')

        self._input_checker = Thread(target=self._check_buffer)
        self._output_checker = Thread(target=self._check_message)
        self._document_syncer = Thread(target=self._check_document_sync)

        self._should_check_buffer = Semaphore(0)
        self._buffer_check_completed = Event()
        self._read_write_check = Lock()

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
            self._agent.stdin.write(m.serialize(message))
            self._agent.stdin.write("\n")
            self._agent.stdin.flush()

        print "Bound agent to port: {}".format(self._agent_port)

        self._output_checker.start()

    def _check_document_sync(self):
        global is_active
        while is_active:
            with self._read_write_check:
                if not is_active:
                    break

                current_buffer = vim.current.buffer[:]
                message = m.CheckDocumentSync(current_buffer)

                self._agent.stdin.write(m.serialize(message))
                self._agent.stdin.write("\n")
                self._agent.stdin.flush()

            sleep(0.5)

    def _shut_down_agent(self):
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self):
        with self._read_write_check:
            # Allow the user input to be checked.
            self._buffer_check_completed.clear()
            self._should_check_buffer.release()
            self._buffer_check_completed.wait()

    def _check_buffer(self):
        while True:
            # Wait on a signal from the autocommand that the text has changed
            self._should_check_buffer.acquire()
            global is_active
            if not is_active:
              break

            # The read_write_check lock is held by the signalling thread
            current_buffer = vim.current.buffer[:]

            if len(current_buffer) != len(self._buffer):
                self._send_patches(current_buffer)
            else:
                for i in range(len(current_buffer)):
                    if current_buffer[i] != self._buffer[i]:
                        self._send_patches(current_buffer)
                        break

            self._buffer = current_buffer

            self._buffer_check_completed.set()


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
        try :
            prev_contents = os.linesep.join(self._buffer)
            curr_contents = os.linesep.join(current_buffer)
            diff_patches = patch.patch_make(prev_contents, curr_contents)

            patches = []
            for p in diff_patches:
                start_index = p.start1
                end_index = p.start1 + p.length1

                start_rc = index_to_point(self._buffer, start_index)
                end_rc = index_to_point(self._buffer, end_index)

                text = []
                for (op, data) in p.diffs:
                    if op == diff_match_patch.DIFF_INSERT or op == diff_match_patch.DIFF_EQUAL:
                        text.append(data)
                text = "".join(text)

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
            if isinstance(message, m.ApplyText):
                with self._read_write_check:
                    vim.current.buffer[:] = message.contents
                    # TODO: Send ack back to agent.
                    self._buffer = vim.current.buffer[:]
                    vim.command(":redraw")

            elif isinstance(message, m.WriteRequest):
                # Acquire the lock to prevent further writes
                self._read_write_check.acquire()
                vim.command(":set nomodifiable")
                self._agent.stdin.write(m.serialize(m.WriteRequestAck()))
                self._agent.stdin.write("\n")
                self._agent.stdin.flush()

            elif isinstance(message, m.ApplyPatches):
                # read_write_check lock should already be acquired
                for patch in message.patch_list:
                    start = patch["oldStart"]
                    end = patch["oldEnd"]
                    text = patch["newText"]

                    current_buffer = vim.current.buffer[:]
                    before_lines = current_buffer[:start["row"]]
                    after_lines = current_buffer[end["row"] + 1:]

                    before_in_new_line = current_buffer[start["row"]][:start["column"]]
                    after_in_new_line = current_buffer[end["row"]][end["column"]:]

                    new_lines = text.split(os.linesep)
                    if len(new_lines) > 0:
                        new_lines[0] = before_in_new_line + new_lines[0]
                    else:
                        new_lines = [before_in_new_line]

                    new_lines[-1] = new_lines[-1] + after_in_new_line

                    vim.command(":set modifiable")
                    vim.current.buffer[:] = \
                        before_lines + new_lines + after_lines
                    vim.command(":set nomodifiable")

                self._buffer = vim.current.buffer[:]
                vim.command(":redraw")

                # Enable editing again
                vim.command(":set modifiable")
                self._read_write_check.release()
        except:
            error()

    def _set_up_autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd TextChanged <buffer> py tandem_agent.check_buffer()')
        vim.command('autocmd TextChangedI <buffer> py tandem_agent.check_buffer()')
        vim.command('autocmd VimLeave * py tandem_agent.stop()')


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

        self._input_checker.start()
        # self._document_syncer.start()
        self._set_up_autocommands()

        if self._connect_to is None:
            self.check_buffer()

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
        # if self._document_syncer.isAlive():
            # if sself._document_syncer.join()


tandem_agent = TandemPlugin()

EOF

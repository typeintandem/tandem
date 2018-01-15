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

from subprocess import Popen, PIPE
from threading import Thread, Semaphore

import vim

# For now, add the tandem agent path to the system path so that we can use the
# existing messages protocol implementation
tandem_agent_path = os.path.abspath('../../agent')
if tandem_agent_path not in sys.path:
    sys.path.insert(0, tandem_agent_path)

import tandem.protocol.editor.messages as m

is_active = False

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
        self._should_check_buffer = Semaphore(0)

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
        else:
            print "Bound host to port: {}".format(self._agent_port)

        if not self._is_host:
            self._output_checker.start()

    def _shut_down_agent(self):
        self._agent.stdin.close()
        self._agent.terminate()
        self._agent.wait()

    def check_buffer(self):
        self._should_check_buffer.release()

    def _check_buffer(self):
        while True:
            self._should_check_buffer.acquire()
            if not is_active:
              break

            current_buffer = vim.current.buffer[:]

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
            raise ValueError
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
        """
        Invocation precondition is that there is a difference between the two
        buffers. Creates and sends update packet corresponding to the change.
        """
        top = 0
        old_bottom = len(self._buffer) - 1
        new_bottom = len(current_buffer) - 1

        start, end, text = (None,)*3

        while True:
          if top > old_bottom or top > new_bottom or \
                  self._buffer[top] != current_buffer[top]:
              break

          top += 1

        if top > old_bottom:
            # everything was the same in the old buffer. We must have added
            # lines to the new buffer.
            # need to add new line at end of previous line
            if top == 0:
                start = (top, 0)
                end = (top, 0)
            else:
                line_end = len(current_buffer[top - 1])
                start = (top - 1, line_end)
                end = (top - 1, line_end)
            text = os.linesep + os.linesep.join(current_buffer[top:new_bottom + 1])
        elif top > new_bottom:
            # everything was the same in the new buffer. We must have deleted
            # lines in the old buffer.
            start = (top, 0)
            end = (old_bottom, len(self._buffer[old_bottom]))
            text = ""
        else:
            # otherwise, we now have the point at which the lines are
            # different b/w the two buffers. if we repeat the process from the
            # bottom, we can find the rows in which the text differs.

            while True:
              if old_bottom < top or new_bottom < top or \
                      self._buffer[old_bottom] != current_buffer[new_bottom]:
                  break

              old_bottom -= 1
              new_bottom -= 1

            if old_bottom < top:
                # added text to the old buffer
                # Add to start of previous line if possible, or top of document
                if top == 0:
                    start = (top, 0)
                    end = (top, 0)
                else:
                    line_end = len(current_buffer[top - 1])
                    start = (top - 1, line_end)
                    end = (top - 1, line_end)
                text = os.linesep + (os.linesep).join(current_buffer[top:new_bottom + 1])
            elif new_bottom < top:
                # removed text from old buffer
                start = (top, 0)
                if old_bottom == top and len(self._buffer[top]) == 0 and len(self._buffer) > old_bottom + 1:
                    # removed empty line. Remove up to the start of the next line.
                    end = (old_bottom + 1, 0)
                else:
                    end = (old_bottom, len(self._buffer[old_bottom]))
                text = ""
            else:
                # otherwise, it's a one-line change. Replace the whole row.
                # TODO: This is false. not always a one line change (paste multiple lines at once)
                start = (top, 0)
                end = (top, len(self._buffer[top]))
                text = current_buffer[top]
                if top >= len(self._buffer):
                    text = os.linesep + tex

        patches = m.NewPatches([
            self._create_patch(start, end, text),
        ])
        self._agent.stdin.write(m.serialize(patches))
        self._agent.stdin.write(os.linesep)
        self._agent.stdin.flush()


    def _check_message(self):
        while True:
            line = self._agent.stdout.readline()
            if line == "":
                break
            self._handle_message(line)

    def _handle_message(self, msg):
        try:
            message = m.deserialize(msg)
            if isinstance(message, m.ApplyText):
                vim.current.buffer[:] = message.contents
            elif isinstance(message, m.ApplyPatches):
                for patch in message.patch_list:
                    start = patch["oldStart"]
                    end = patch["oldEnd"]

                    # rows before the changed
                    before_change = vim.current.buffer[:start["row"]]
                    # rows after the change
                    after_change = vim.current.buffer[end["row"] + 1:]
                    # the patch to apply, split into rows
                    new_text = patch["newText"]
                    if new_text == os.linesep:
                        new_lines = [os.linesep]
                    else:
                        new_lines = new_text.splitlines()

                    before_in_new_line = vim.current.buffer[start["row"]][:start["column"]]
                    after_in_new_line = vim.current.buffer[end["row"]][end["column"]:]
                    if len(new_lines) > 0:
                        # prepend contents from buffer to first line
                        new_lines[0] = before_in_new_line + new_lines[0]
                    elif before_in_new_line != '':
                        new_lines = [before_in_new_line]

                    if len(new_lines) > 0:
                        # append contents from buffer to last line
                        new_lines[-1] = new_lines[-1] + after_in_new_line
                        tail = [''] if new_lines[-1].endswith(os.linesep) else []
                        new_lines = new_lines[:-1] + new_lines[-1].splitlines() + tail
                    elif after_in_new_line != '':
                        new_lines = [after_in_new_line]

                    vim.current.buffer[:] = \
                        before_change + new_lines + after_change

            self._buffer = vim.current.buffer[:]
            vim.command(":redraw")
        except:
            print "An error occurred."
            raise

    def _send_user_changed(self, text):
        message = m.UserChangedEditorText(text)
        self._agent.stdin.write(m.serialize(message))
        self._agent.stdin.write(os.linesep)
        self._agent.stdin.flush()

    def _set_up_autocommands(self):
        vim.command(':autocmd!')
        vim.command('autocmd CursorMoved <buffer> py tandem_agent.check_buffer()')
        vim.command('autocmd CursorMovedI <buffer> py tandem_agent.check_buffer()')
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

        if self._is_host and is_running(self._input_checker):
            self._input_checker.join()
        elif not self._is_host and is_running(self._output_checker):
            self._output_checker.join()


def is_running(thread):
    return thread is not None and thread.isAlive()


tandem_agent = TandemPlugin()

EOF

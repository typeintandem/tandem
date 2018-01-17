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

DEBUG = False
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
        self._document_syncer = Thread(target=self._check_document_sync)
        self._should_check_buffer = Semaphore(0)
        self._ui = Semaphore(0)
        self._read_write_check = Semaphore(1)

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

    def _check_document_sync(self):
        while is_active:
            current_buffer = vim.current.buffer[:]
            message = m.CheckDocumentSync(current_buffer)
            self._agent.stdin.write(m.serialize(message))
            self._agent.stdin.write("\n")
            self._agent.stdin.flush()
            sleep(1)

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
            if not is_active:
              break
            # Wait until the output checker is not applying patches.
            self._read_write_check.acquire()
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
            # Allow the next input/output checker thread to continue.
            self._read_write_check.release()

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
        line = 0
        patches = []

        changes = diff(self._buffer, current_buffer);
        if DEBUG:
            print "============"
            print "curr_buffer: ", current_buffer
        for change in changes:
            operation = change[0]
            lines_affected = change[1]
            if DEBUG:
                print operation, " ", lines_affected

            if operation == '-':
                # Delete from start of current line to end of last specified line.
                if line == 0:
                    start = (0, 0)
                    if len(self._buffer) == 1:
                        end = (0, len(self._buffer[0]))
                    else:
                        end = (1, 0)
                else:
                    start = (line - 1, len(self._buffer[line - 1]))
                    end_line = line + len(lines_affected) - 1
                    end = (end_line, len(self._buffer[end_line]))
                text = ""
                patches.append(
                  self._create_patch(start, end, text)
                )
                if DEBUG:
                    print "start: ", start
                    print "end: ", end
                    print "text: ", text

            elif operation == '+':
                start = (line, 0)
                end = start
                # Insert text followed by new lines.
                text = os.linesep.join(lines_affected) + os.linesep
                patches.append(
                  self._create_patch(start, end, text)
                )
                # Shift all future row numbers
                line = line + len(lines_affected)
            elif operation == '=':
                # No patches, but increment alll future row numbers
                line = line + len(lines_affected)
            else:
                raise

        # Filter erroneous patches.
        patches = [p for p in patches if p is not None]
        if len(patches) > 0:
            message = m.NewPatches(patches)
            self._agent.stdin.write(m.serialize(message))

            self._agent.stdin.write(os.linesep)
            self._agent.stdin.flush()

            if DEBUG:
                print "Sent patches: " + str(message.patch_list)

    def _check_message(self):
        while True:
            line = self._agent.stdout.readline()
            if line == "":
                break
            self._handle_message(line)

    def _handle_message(self, msg):
        try:
            # Wait until the input checker thread is done.
            self._read_write_check.acquire()
            message = m.deserialize(msg)
            if isinstance(message, m.ApplyText):
                vim.current.buffer[:] = message.contents
            elif isinstance(message, m.ApplyPatches):
                if DEBUG:
                    print "============="
                    print "Received patches: " + str(message.patch_list)
                for patch in message.patch_list:
                    start = patch["oldStart"]
                    end = patch["oldEnd"]
                    text = patch["newText"]

                    # For now, assume deletion is whole line and insertion is at a single point.
                    # Modifying the first row only (only thing that exists)
                    if start["row"] == 0 and end["row"] == 0:
                        before_row = 0
                    else:
                        before_row = start["row"] + 1

                    before = vim.current.buffer[:before_row]

                    after_row = end["row"] if (text == os.linesep) else end["row"] + 1
                    after = vim.current.buffer[after_row:]

                    new_lines = text.splitlines() if text != "" else []

                    if DEBUG:
                        print "buffer: ", vim.current.buffer[:]
                        print "start: ", start
                        print "end: ", end
                        print "after_row: ", after_row
                        if text == "":
                            print "text: emptystring"
                        elif text == os.linesep:
                            print "text: linesep"
                        else:
                            print "text: ", text
                        print "before: ", before
                        print "new_lines: ", new_lines
                        print "after: ", after
                    vim.current.buffer[:] = before + new_lines + after

            self._buffer = vim.current.buffer[:]
            vim.command(":redraw")
            # Allow the next input/output checker thread to continue.
            self._read_write_check.release()
        except:
            # Release the lock in case of exception.
            self._read_write_check.release()
            print "An error occurred."
            if DEBUG:
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



# ===================================
#              UTILS
# ===================================
# Unmodified from
# https://github.com/paulgb/simplediff/blob/master/python/simplediff/__init__.py
'''
Simple Diff for Python version 1.0

Annotate two versions of a list with the values that have been
changed between the versions, similar to unix's `diff` but with
a dead-simple Python interface.

(C) Paul Butler 2008-2012 <http://www.paulbutler.org/>
May be used and distributed under the zlib/libpng license
<http://www.opensource.org/licenses/zlib-license.php>
'''

__all__ = ['diff', 'string_diff', 'html_diff']
__version__ = '1.0'


def diff(old, new):
    '''
    Find the differences between two lists. Returns a list of pairs, where the
    first value is in ['+','-','='] and represents an insertion, deletion, or
    no change for that list. The second value of the pair is the list
    of elements.

    Params:
        old     the old list of immutable, comparable values (ie. a list
                of strings)
        new     the new list of immutable, comparable values

    Returns:
        A list of pairs, with the first part of the pair being one of three
        strings ('-', '+', '=') and the second part being a list of values from
        the original old and/or new lists. The first part of the pair
        corresponds to whether the list of values is a deletion, insertion, or
        unchanged, respectively.

    Examples:
        >>> diff([1,2,3,4],[1,3,4])
        [('=', [1]), ('-', [2]), ('=', [3, 4])]

        >>> diff([1,2,3,4],[2,3,4,1])
        [('-', [1]), ('=', [2, 3, 4]), ('+', [1])]

        >>> diff('The quick brown fox jumps over the lazy dog'.split(),
        ...      'The slow blue cheese drips over the lazy carrot'.split())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('=', ['The']),
         ('-', ['quick', 'brown', 'fox', 'jumps']),
         ('+', ['slow', 'blue', 'cheese', 'drips']),
         ('=', ['over', 'the', 'lazy']),
         ('-', ['dog']),
         ('+', ['carrot'])]

    '''

    # Create a map from old values to their indices
    old_index_map = dict()
    for i, val in enumerate(old):
        old_index_map.setdefault(val,list()).append(i)

    # Find the largest substring common to old and new.
    # We use a dynamic programming approach here.
    # 
    # We iterate over each value in the `new` list, calling the
    # index `inew`. At each iteration, `overlap[i]` is the
    # length of the largest suffix of `old[:i]` equal to a suffix
    # of `new[:inew]` (or unset when `old[i]` != `new[inew]`).
    #
    # At each stage of iteration, the new `overlap` (called
    # `_overlap` until the original `overlap` is no longer needed)
    # is built from the old one.
    #
    # If the length of overlap exceeds the largest substring
    # seen so far (`sub_length`), we update the largest substring
    # to the overlapping strings.

    overlap = dict()
    # `sub_start_old` is the index of the beginning of the largest overlapping
    # substring in the old list. `sub_start_new` is the index of the beginning
    # of the same substring in the new list. `sub_length` is the length that
    # overlaps in both.
    # These track the largest overlapping substring seen so far, so naturally
    # we start with a 0-length substring.
    sub_start_old = 0
    sub_start_new = 0
    sub_length = 0

    for inew, val in enumerate(new):
        _overlap = dict()
        for iold in old_index_map.get(val,list()):
            # now we are considering all values of iold such that
            # `old[iold] == new[inew]`.
            _overlap[iold] = (iold and overlap.get(iold - 1, 0)) + 1
            if(_overlap[iold] > sub_length):
                # this is the largest substring seen so far, so store its
                # indices
                sub_length = _overlap[iold]
                sub_start_old = iold - sub_length + 1
                sub_start_new = inew - sub_length + 1
        overlap = _overlap

    if sub_length == 0:
        # If no common substring is found, we return an insert and delete...
        return (old and [('-', old)] or []) + (new and [('+', new)] or [])
    else:
        # ...otherwise, the common substring is unchanged and we recursively
        # diff the text before and after that substring
        return diff(old[ : sub_start_old], new[ : sub_start_new]) + \
               [('=', new[sub_start_new : sub_start_new + sub_length])] + \
               diff(old[sub_start_old + sub_length : ],
                       new[sub_start_new + sub_length : ])

# ===================================
#               MAIN
# ===================================

tandem_agent = TandemPlugin()

EOF

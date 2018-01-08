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

com! -nargs=* TandemStop py tandem_agent.stop(<f-args>)

python << EOF

import os
import sys
import random
from time import sleep

from subprocess import Popen, PIPE
from threading import Thread, Event

import vim

# For now, add the tandem agent path to the system path so that we can use the
# existing messages protocol implementation
tandem_agent_path = os.path.abspath('../../agent')
if tandem_agent_path not in sys.path:
    sys.path.insert(0, tandem_agent_path)

import tandem.protocol.editor.messages as m

should_exit = False

def start_agent(extra_args=None):
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


class PluginManager:

    def __init__(self, curr_buffer):
        self._buffer = curr_buffer

        self._main_thread = Thread(target=self._start_agents)

        self._input_checker = Thread(target=self._check_buffer)
        self._output_checker = Thread(target=self._check_message)

    def _start_agents(self):
        agent_port = get_string_port()
        self._agent = start_agent([
            "--port",
            agent_port,
            "--log-file",
            "/tmp/tandem-agent-{}.log".format(agent_port),
        ])

        if not self._is_host:
            # Wait for the agents to start accepting connections
            sleep(1)

            message = m.ConnectTo(self._host_ip, int(self._host_port))
            self._agent.stdin.write(m.serialize(message))
            self._agent.stdin.write("\n")
            self._agent.stdin.flush()
        else:
            print "Host Port:", agent_port

        if self._is_host:
            self._input_checker.start()
        else:
            self._output_checker.start()

    def _shut_down_agents(self):
        # Shut down the agents
        self._agent.stdin.close()
        self._agent.terminate()

        self._agent.wait()

    def _check_buffer(self):
        while not should_exit:
            current_buffer = vim.current.buffer[:]

            # perform check
            # first case should never happen
            if current_buffer is None or \
                    len(current_buffer) != len(self._buffer):
                send_user_changed(self._agent.stdin, current_buffer)
            else:
                should_send = False
                for i in range(len(current_buffer)):
                    if current_buffer[i] != self._buffer[i]:
                        should_send = True
                        break
                if should_send:
                    send_user_changed(self._agent.stdin, current_buffer)

            self._buffer = current_buffer

            sleep(1)

    def _check_message(self):
        while True:
            line = self._agent.stdout.readline()
            if line == '':
                break
            self._handle_message(line)

    def _handle_message(self, msg):
        try:
            print msg
            message = m.deserialize(msg)
            if isinstance(message, m.ApplyText):
                print message.contents[0]
                vim.current.buffer[:] = message.contents
                vim.command(':redraw')
        except m.EditorProtocolMarshalError:
            pass
        except:
            pass

    def start(self, is_host, host_ip, host_port):
        self._is_host = is_host
        if not is_host:
            self._host_ip = host_ip
            self._host_port = host_port

        self._main_thread.start()

    def stop(self):
        self._shut_down_agents()

        self._main_thread.join()

        if self._is_host:
            global should_exit
            should_exit = True
            self._input_checker.join()
        else:
            self._output_checker.join()


def send_user_changed(agent_stdin, text):
    message = m.UserChangedEditorText(text)
    agent_stdin.write(m.serialize(message))
    agent_stdin.write("\n")
    agent_stdin.flush()


class TandemPlugin():
    def __init__(self):
        # Sends message from agent1 to agent2
        self._plugin_manager = PluginManager(vim.current.buffer[:])

    def start(self, is_host, ip=None, port=None):
         self._plugin_manager.start(is_host == 'h', ip, port)

    def stop(self):
        self._plugin_manager.stop()
        print "closed succesfully"

    def handle_command(self):
        pass

tandem_agent = TandemPlugin()

EOF

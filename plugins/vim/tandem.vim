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


def get_string_ports():
    starting_port = random.randint(60600, 62600)
    port1 = str(starting_port)
    port2 = str(starting_port+1)
    return port1, port2


class PluginManager:

    def __init__(self, curr_buffer):
        self._buffer = curr_buffer
        self._main_thread = Thread(target=self._start_agents)
        self._input_checker = Thread(target=self._check_buffer)
        self._output_checker = Thread(target=self._check_message)

    def _start_agents(self):
        agent1_port, agent2_port = get_string_ports()

        self._agent1 = start_agent(["--port", agent1_port])
        self._agent2 = start_agent([
            "--port",
            agent2_port,
            "--log-file",
            "/tmp/tandem-agent-2.log",
        ])

        # Wait for the agents to start accepting connections
        sleep(1)

        message = m.ConnectTo("localhost", int(agent1_port))
        self._agent2.stdin.write(m.serialize(message))
        self._agent2.stdin.write("\n")
        self._agent2.stdin.flush()

        # Wait for the pings
        sleep(2)

        # Assume we got dem pings
        self._input_checker.start()
        self._output_checker.start()

    def _shut_down_agents(self):
        # Shut down the agents
        self._agent1.stdin.close()
        self._agent1.terminate()
        self._agent2.stdin.close()
        self._agent2.terminate()

        self._agent1.wait()
        self._agent2.wait()

    def _check_buffer(self):
        while not should_exit:
            current_buffer = vim.current.buffer[:]

            # perform check
            # first case should never happen
            if current_buffer is None or \
                    len(current_buffer) != len(self._buffer):
                send_user_changed(self._agent1.stdin, current_buffer)
            else:
                should_send = False
                for i in range(len(current_buffer)):
                    if current_buffer[i] != self._buffer[i]:
                        should_send = True
                        break
                if should_send:
                    send_user_changed(self._agent1.stdin, current_buffer)

            self._buffer = current_buffer

            sleep(1)

    def _check_message(self):
        while True:
            line = self._agent2.stdout.readline()
            if line == '':
                break
            print "Received:", line

    def start(self):
        self._main_thread.start()

    def stop(self):
        self._shut_down_agents()

        self._main_thread.join()

        global should_exit
        should_exit = True
        self._input_checker.join()

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

    def start(self):
        self._plugin_manager.start()

    def stop(self):
        self._plugin_manager.stop()
        print "closed succesfully"

    def handle_command(self):
        pass

tandem_agent = TandemPlugin()

EOF

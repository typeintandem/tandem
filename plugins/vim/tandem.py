import os
import sys

from subprocess import Popen, PIPE

# For now, add the tandem agent path to the system path so that we can use the
# existing messages protocol implementation
tandem_agent_path = os.path.abspath('../../agent')
if tandem_agent_path not in sys.path:
    sys.path.insert(0, tandem_agent_path)

import tandem.protocol.editor.messages as m


def start_agent():
    return Popen(
        ["python3", "../../agent/main.py"],
        stdin=PIPE,
        stdout=PIPE,
    )


def send_user_changed(agent_stdin, text):
    message = m.UserChangedEditorText(text)
    agent_stdin.write(m.serialize(message))
    agent_stdin.write("\n")
    agent_stdin.flush()


def print_raw_message(agent_stdout):
    resp = agent_stdout.readline()
    print "Received: " + resp


def main():
    # Spawn the agent process
    agent = start_agent()

    # Send the agent a dummy message
    send_user_changed(agent.stdin, "Hello world!")

    # The agent currently just echos messages so just print the response
    print_raw_message(agent.stdout)

    # Repeat
    send_user_changed(agent.stdin, "Hello world again!")
    print_raw_message(agent.stdout)

    # Stop the agent and wait for it to shutdown gracefully
    agent.stdin.close()
    agent.terminate()
    agent.wait()


if __name__ == "__main__":
    main()

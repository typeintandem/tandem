import sys
import time
import random
from subprocess import Popen, PIPE
import tandem.protocol.editor.messages as m


def start_agent(extra_args=None):
    if extra_args is None:
        extra_args = []
    return Popen(
        ["python3", "main.py"] + extra_args,
        stdin=PIPE,
        stdout=PIPE,
        encoding="utf-8",
    )


def send_user_changed(agent_stdin, text):
    message = m.UserChangedEditorText(text)
    agent_stdin.write(m.serialize(message))
    agent_stdin.write("\n")
    agent_stdin.flush()


def print_raw_message(agent_stdout):
    resp = agent_stdout.readline()
    print("Received: " + resp)


def get_string_ports():
    starting_port = random.randint(60600, 62600)
    port1 = str(starting_port)
    port2 = str(starting_port+1)
    return port1, port2


def ping_test():
    """
    Starts 2 agents and checks that they can establish
    a connection to eachother and exchange a ping message.
    """
    agent1_port, agent2_port = get_string_ports()

    agent1 = start_agent(["--port", agent1_port])
    agent2 = start_agent([
        "--port",
        agent2_port,
        "--log-file",
        "/tmp/tandem-agent-2.log",
    ])

    # Wait for the agents to start accepting connections
    time.sleep(1)

    message = m.ConnectTo("localhost", int(agent1_port))
    agent2.stdin.write(m.serialize(message))
    agent2.stdin.write("\n")
    agent2.stdin.flush()

    # Wait for the pings
    time.sleep(2)

    agent1.stdin.close()
    agent1.terminate()
    agent2.stdin.close()
    agent2.terminate()

    agent1.wait()
    agent2.wait()


def text_transfer_test():
    """
    Tests the Milestone 1 flow by starting 2 agents and
    transfering text data from one agent to the other.

    1. Instruct agent 2 to connect to agent 1
    2. Send a "text changed" message to agent 1
       (simulating what the plugin would do)
    3. Expect an "apply text" message to be "output" by agent 2
       (this would be an instruction to the plugin to change
       the editor's text buffer)
    """
    agent1_port, agent2_port = get_string_ports()

    agent1 = start_agent(["--port", agent1_port])
    agent2 = start_agent([
        "--port",
        agent2_port,
        "--log-file",
        "/tmp/tandem-agent-2.log",
    ])

    # Wait for the agents to start accepting connections
    time.sleep(1)

    message = m.ConnectTo("localhost", int(agent1_port))
    agent2.stdin.write(m.serialize(message))
    agent2.stdin.write("\n")
    agent2.stdin.flush()

    # Wait for the pings
    time.sleep(2)

    # Simulate a text buffer change - the plugin notifes agent1 that
    # the text buffer has changed
    send_user_changed(agent1.stdin, ["Hello world!"])

    # Expect agent2 to receive a ApplyText message
    print_raw_message(agent2.stdout)

    # Repeat
    send_user_changed(agent1.stdin, ["Hello world again!"])
    print_raw_message(agent2.stdout)

    # Shut down the agents
    agent1.stdin.close()
    agent1.terminate()
    agent2.stdin.close()
    agent2.terminate()

    agent1.wait()
    agent2.wait()


def main():
    text_transfer_test()


if __name__ == "__main__":
    main()

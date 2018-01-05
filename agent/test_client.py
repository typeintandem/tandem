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


def basic_echo():
    # Spawn the agent process
    agent = start_agent()

    # Send the agent a dummy message
    send_user_changed(agent.stdin, "Hello world!")

    # The agent currently just echos messages
    # so just print the response
    print_raw_message(agent.stdout)

    # Repeat
    send_user_changed(agent.stdin, "Hello world again!")
    print_raw_message(agent.stdout)

    # Stop the agent and wait for it to
    # shutdown gracefully
    agent.stdin.close()
    agent.terminate()
    agent.wait()


def ping_test():
    starting_port = random.randint(60600, 61600)
    agent1_port = str(starting_port)
    agent2_port = str(starting_port+1)

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


def main():
    ping_test()


if __name__ == "__main__":
    main()

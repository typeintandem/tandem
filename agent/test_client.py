import os
import time
import random
from subprocess import Popen, PIPE
import tandem.agent.protocol.messages.editor as m
from tandem.agent.configuration import BASE_DIR


def start_agent(extra_args=None):
    if extra_args is None:
        extra_args = []
    return Popen(
        ["python3", os.path.join(BASE_DIR, "main.py")] + extra_args,
        stdin=PIPE,
        stdout=PIPE,
        encoding="utf-8",
    )


def send_user_changed(agent_stdin, text):
    message = m.UserChangedEditorText(text)
    agent_stdin.write(m.serialize(message))
    agent_stdin.write("\n")
    agent_stdin.flush()


def send_new_patches(agent_stdin, start, end, text):
    patches = m.NewPatches([{
        "start": start,
        "end": end,
        "text": text,
    }])
    agent_stdin.write(m.serialize(patches))
    agent_stdin.write("\n")
    agent_stdin.flush()


def send_request_write_ack(agent_stdin, seq):
    agent_stdin.write(m.serialize(m.WriteRequestAck(seq)))
    agent_stdin.write("\n")
    agent_stdin.flush()


def print_raw_message(agent_stdout):
    resp = agent_stdout.readline()
    print("Received: " + resp)


def extract_message(agent_stdout):
    resp = agent_stdout.readline()
    return m.deserialize(resp)


def get_string_ports():
    starting_port = random.randint(60600, 62600)
    port1 = str(starting_port)
    port2 = str(starting_port + 1)
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


def crdt_test():
    """
    Tests the Milestone 2 flow.
    1. Agent 1 makes a local change
    2. Check that Agent 2 received the changes
    3. Repeat
    4. Agent 2 makes a local change
    5. Check that Agent 1 received the changes
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

    # Wait for connection
    time.sleep(1)

    # Simulate a text buffer change - the plugin notifes agent1 that
    # the text buffer has changed
    send_new_patches(
        agent1.stdin,
        {"row": 0, "column": 0},
        {"row": 0, "column": 0},
        "Hello world!",
    )
    print("Agent 1 made an edit")

    # Simulate a text buffer change - the plugin notifes agent1 that
    # the text buffer has changed
    send_new_patches(
        agent1.stdin,
        {"row": 0, "column": 12},
        {"row": 0, "column": 0},
        " Hello world again!",
    )
    print("Agent 1 made a second edit")

    # The agent should not resend the request write message
    time.sleep(1)

    # Expect agent2 to receive a "Request Write" message
    print_raw_message(agent2.stdout)

    # Allow the plugin to apply the remote changes
    send_request_write_ack(agent2.stdin, 0)

    # Expect agent2 to get the changes
    print_raw_message(agent2.stdout)

    # Simulate an edit that occurs on agent2's machine
    send_new_patches(
        agent2.stdin,
        {"row": 0, "column": 0},
        {"row": 0, "column": 0},
        "Agent 2 says hi! ",
    )
    print("Agent 2 made an edit")

    # Expect agent1 to receive a RequestWrite message
    print_raw_message(agent1.stdout)

    # Allow changes to be applied
    send_request_write_ack(agent1.stdin, 0)

    # Expect to receive the text patches
    print_raw_message(agent1.stdout)

    # Simulate an edit that occurs on agent2's machine
    send_new_patches(
        agent2.stdin,
        {"row": 0, "column": 0},
        {"row": 0, "column": 0},
        "Agent 2 says hi again! ",
    )
    print("Agent 2 made a second edit!")

    # Expect agent1 to receive a RequestWrite message
    print_raw_message(agent1.stdout)

    # Allow changes to be applied
    send_request_write_ack(agent1.stdin, 1)

    # Expect to receive the text patches
    print_raw_message(agent1.stdout)

    time.sleep(2)

    # Shut down the agents
    agent1.stdin.close()
    agent1.terminate()
    agent2.stdin.close()
    agent2.terminate()

    agent1.wait()
    agent2.wait()


def hole_punch_test():
    agent1_port, agent2_port = get_string_ports()
    agent3_port = str(int(agent2_port) + 1)

    agent1 = start_agent(["--port", agent1_port])
    agent2 = start_agent([
        "--port",
        agent2_port,
        "--log-file",
        "/tmp/tandem-agent-2.log",
    ])
    agent3 = start_agent([
        "--port",
        agent3_port,
        "--log-file",
        "/tmp/tandem-agent-3.log",
    ])

    # Wait for the agents to start up
    time.sleep(1)

    host_session = m.HostSession()
    agent1.stdin.write(m.serialize(host_session))
    agent1.stdin.write("\n")
    agent1.stdin.flush()

    session_info = extract_message(agent1.stdout)
    print("Session ID: {}".format(session_info.session_id))

    join_session = m.JoinSession(session_id=session_info.session_id)
    agent2.stdin.write(m.serialize(join_session))
    agent2.stdin.write("\n")
    agent2.stdin.flush()
    agent3.stdin.write(m.serialize(join_session))
    agent3.stdin.write("\n")
    agent3.stdin.flush()

    time.sleep(5)

    # Shut down the agents
    agent1.stdin.close()
    agent1.terminate()
    agent2.stdin.close()
    agent2.terminate()
    agent3.stdin.close()
    agent3.terminate()

    agent1.wait()
    agent2.wait()
    agent3.wait()


def main():
    hole_punch_test()


if __name__ == "__main__":
    main()

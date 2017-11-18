from tandem.executables.agent import TandemAgent
import signal


agent = None


def signal_handler(signal, frame):
    global agent
    if agent is None:
        return
    agent.stop()


def main():
    global agent
    signal.signal(signal.SIGINT, signal_handler)
    agent = TandemAgent()

    print("Starting the Tandem Agent. Press Ctrl-C and then Ctrl-D to exit.")
    agent.start()


if __name__ == "__main__":
    main()

import signal
import logging
import threading
from tandem.executables.agent import TandemAgent

should_shutdown = threading.Event()


def signal_handler(signal, frame):
    global should_shutdown
    should_shutdown.set()


def set_up_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M',
        filename='/tmp/tandem-agent.log',
        filemode='w',
    )


def main():
    set_up_logging()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the agent until asked to terminate
    with TandemAgent() as agent:
        should_shutdown.wait()


if __name__ == "__main__":
    main()

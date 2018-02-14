import signal
import logging
import threading
import argparse
from tandem.agent.executables.agent import TandemAgent

should_shutdown = threading.Event()


def signal_handler(signal, frame):
    global should_shutdown
    should_shutdown.set()


def set_up_logging(log_location):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M",
        filename=log_location,
        filemode="w",
    )


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="Starts the Tandem agent.")
    parser.add_argument(
        "--host",
        default="",
        help="The host address to bind to.",
    )
    parser.add_argument(
        "--port",
        default=0,
        type=int,
        help="The port to listen on.",
    )
    parser.add_argument(
        "--log-file",
        default="/tmp/tandem-agent.log",
        help="The location of the log file.",
    )
    args = parser.parse_args()

    set_up_logging(args.log_file)

    # Run the agent until asked to terminate
    with TandemAgent(args.host, args.port):
        should_shutdown.wait()


if __name__ == "__main__":
    main()

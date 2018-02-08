import signal
import logging
import threading
import argparse
from tandem.rendezvous.executables.rendezvous import TandemRendezvous

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

    parser = argparse.ArgumentParser(description="Starts the Tandem rendezvous server.")
    parser.add_argument(
        "--host",
        default="localhost",
        help="The host address to bind to.",
    )
    parser.add_argument(
        "--port",
        default=60000,
        type=int,
        help="The port to listen on.",
    )
    parser.add_argument(
        "--log-file",
        default="/tmp/tandem-rendezvous.log",
        help="The location of the log file.",
    )
    args = parser.parse_args()

    set_up_logging(args.log_file)

    # Run the agent until asked to terminate
    with TandemRendezvous(args.host, args.port) as agent:
        should_shutdown.wait()


if __name__ == "__main__":
    main()

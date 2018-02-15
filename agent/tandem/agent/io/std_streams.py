import sys
import logging
from tandem.agent.io.base import InterfaceDataBase, InterfaceBase


class STDData(InterfaceDataBase):
    pass


class STDStreams(InterfaceBase):
    def __init__(self, handler_function):
        super(STDStreams, self).__init__(handler_function)

    def stop(self):
        super(STDStreams, self).stop()
        sys.stdout.close()

    def write_io_data(self, io_data):
        sys.stdout.write(io_data.get_data())
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _read_data(self):
        try:
            for line in sys.stdin:
                self._received_data(STDData(line))
        except:
            logging.exception("Exception when reading from stdin:")
            raise

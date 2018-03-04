import sys
import logging
from tandem.shared.io.base import InterfaceDataBase, InterfaceBase


class STDData(InterfaceDataBase):
    pass


class STDStreams(InterfaceBase):
    data_class = STDData

    def __init__(self, handler_function):
        super(STDStreams, self).__init__(handler_function)

    def stop(self):
        super(STDStreams, self).stop()
        sys.stdout.close()

    def write_io_data(self, *args, **kwargs):
        io_data, = args

        sys.stdout.write(io_data.get_data())
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _read_data(self):
        try:
            for line in sys.stdin:
                self._received_data(line)
        except:
            logging.exception("Exception when reading from stdin:")
            raise

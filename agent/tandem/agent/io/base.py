from threading import Thread


class InterfaceDataBase(object):
    def __init__(self, data):
        self._data = data

    def get_data(self):
        return self._data


class InterfaceBase(object):
    def __init__(self, incoming_data_handler):
        self._incoming_data_handler = incoming_data_handler
        self._reader = Thread(target=self._read_data)

    def start(self):
        self._reader.start()

    def stop(self):
        self._reader.join()

    def generate_io_data(self, *args, **kwargs):
        return InterfaceDataBase(*args, **kwargs)

    def write_io_data(self, io_data):
        raise

    def _read_data(self):
        raise

    def _received_data(self, io_data):
        def retrieve_io_data():
            return io_data

        self._incoming_data_handler(retrieve_io_data)

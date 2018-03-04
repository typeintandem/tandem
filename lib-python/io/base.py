from threading import Thread
from tandem.shared.utils.proxy import ProxyUtils


class InterfaceDataBase(object):
    def __init__(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def is_empty(self):
        return self._data is None


class InterfaceBase(object):
    data_class = InterfaceDataBase

    def __init__(self, incoming_data_handler, proxies=[]):
        self._incoming_data_handler = incoming_data_handler
        self._reader = Thread(target=self._read_data)
        self._proxies = proxies
        for proxy in proxies:
            proxy.attach_interface(self)

    def start(self):
        self._reader.start()

    def stop(self):
        self._reader.join()

    def generate_io_data(self, *args, **kwargs):
        new_args, new_kwargs = ProxyUtils.run(
            self._proxies,
            'pre_generate_io_data',
            (args, kwargs),
        )
        return self._generate_io_data(*new_args, **new_kwargs)

    def write_io_data(self, *args, **kwargs):
        new_args, new_kwargs = ProxyUtils.run(
            self._proxies,
            'pre_write_io_data',
            (args, kwargs),
        )
        return self._write_io_data(*new_args, **new_kwargs)

    def _generate_io_data(self, *args, **kwargs):
        return self.data_class(*args, **kwargs)

    def _write_io_data(self, *args, **kwargs):
        raise

    def _read_data(self):
        raise

    def _received_data(self, *args, **kwargs):
        def retrieve_io_data():
            new_args, new_kwargs = ProxyUtils.run(
                self._proxies[::-1],
                'on_retrieve_io_data',
                (args, kwargs),
            )
            if new_args is not None and new_kwargs is not None:
                return self.data_class(*new_args, **new_kwargs)
            else:
                return None

        self._incoming_data_handler(retrieve_io_data)

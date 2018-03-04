class ProxyBase(object):
    def attach_interface(self, interface):
        self._interface = interface

    def on_retrieve_io_data(self, params):
        return params

    def pre_generate_io_data(self, params):
        return params

    def pre_write_io_data(self, params):
        return params

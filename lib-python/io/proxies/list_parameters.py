from tandem.shared.io.proxies.base import ProxyBase


class ListParametersProxy(ProxyBase):
    @staticmethod
    def make_lists(items):
        new_items = []
        for item in items:
            if type(item) is not list:
                item = [item]
            new_items.append(item)
        return new_items

    def pre_generate_io_data(self, params):
        args, kwargs = params
        return (ListParametersProxy.make_lists(args), kwargs)

    def pre_write_io_data(self, params):
        args, kwargs = params
        return (ListParametersProxy.make_lists(args), kwargs)

class ProxyUtils(object):
    @staticmethod
    def run(proxies, method, data):
        for proxy in proxies:
            data = getattr(proxy, method, lambda x: x)(data)

        return data

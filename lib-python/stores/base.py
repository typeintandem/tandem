class StoreBase(object):
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    @classmethod
    def reset_instance(cls):
        cls.instance = None

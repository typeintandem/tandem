import redis

from tandem.settings import REDIS


def Redis():
    return redis.StrictRedis(**REDIS)

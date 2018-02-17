import enum


class ConnectionState(enum.Enum):
    PING = "ping"
    HELLO = "hello"
    WAIT = "wait"
    OPEN = "open"

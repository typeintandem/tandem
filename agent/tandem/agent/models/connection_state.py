import enum


class ConnectionState(enum.Enum):
    HELLO = "hello"
    WAIT = "wait"
    OPEN = "open"

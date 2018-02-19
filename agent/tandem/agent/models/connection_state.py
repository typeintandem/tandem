import enum


class ConnectionState(enum.Enum):
    SYN = "syn"
    WAIT = "wait"
    OPEN = "open"

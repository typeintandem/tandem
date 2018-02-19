import enum


class ConnectionState(enum.Enum):
    SEND_SYN = "syn"
    WAIT_FOR_SYN = "wait"
    OPEN = "open"

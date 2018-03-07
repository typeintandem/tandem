import enum


class ConnectionState(enum.Enum):
    PING = "ping"
    SEND_SYN = "syn"
    WAIT_FOR_SYN = "wait"
    OPEN = "open"
    RELAY = "relay"
    UNREACHABLE = "unreachable"

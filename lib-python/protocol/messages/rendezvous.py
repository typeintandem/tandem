from tandem.shared.protocol.messages.base import (
    ProtocolMessageBase,
    ProtocolMessageTypeBase,
    ProtocolUtilsBase,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class RendezvousProtocolMessageType(ProtocolMessageTypeBase):
    NewSession = "rv-new-session"
    SessionCreated = "rv-session-created"
    ConnectRequest = "rv-connect-request"
    SetupParameters = "rv-setup-parameters"
    Error = "rv-error"


class NewSession(ProtocolMessageBase):
    """
    Sent by an agent to create a new session.
    """
    def __init__(self, **kwargs):
        super(NewSession, self).__init__(
            RendezvousProtocolMessageType.NewSession,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["host_id", "private_address"]


class SessionCreated(ProtocolMessageBase):
    """
    Sent by the server in response to a NewSession request.
    """
    def __init__(self, **kwargs):
        super(SessionCreated, self).__init__(
            RendezvousProtocolMessageType.SessionCreated,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["session_id"]


class ConnectRequest(ProtocolMessageBase):
    """
    Sent by an agent to request to join an existing session.
    """
    def __init__(self, **kwargs):
        super(ConnectRequest, self).__init__(
            RendezvousProtocolMessageType.ConnectRequest,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["session_id", "my_id", "private_address"]


class SetupParameters(ProtocolMessageBase):
    """
    Sent by the server to agents to inform them to connect.
    """
    def __init__(self, **kwargs):
        super(SetupParameters, self).__init__(
            RendezvousProtocolMessageType.SetupParameters,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["session_id", "peer_id", "initiate", "connect_to"]


class Error(ProtocolMessageBase):
    """
    Sent by the server to send an error message.
    """
    def __init__(self, **kwargs):
        super(Error, self).__init__(
            RendezvousProtocolMessageType.Error,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["message"]


class RendezvousProtocolUtils(ProtocolUtilsBase):
    @classmethod
    @staticvalue
    def _protocol_message_constructors(cls):
        return {
            RendezvousProtocolMessageType.NewSession.value:
                NewSession,
            RendezvousProtocolMessageType.SessionCreated.value:
                SessionCreated,
            RendezvousProtocolMessageType.ConnectRequest.value:
                ConnectRequest,
            RendezvousProtocolMessageType.SetupParameters.value:
                SetupParameters,
            RendezvousProtocolMessageType.Error.value: Error,
        }

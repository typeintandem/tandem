from tandem.shared.protocol.messages.base import (
    ProtocolMessageBase,
    ProtocolMessageTypeBase,
    ProtocolUtilsBase,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class RendezvousProtocolMessageType(ProtocolMessageTypeBase):
    ConnectRequest = "rv-connect-request"
    SetupParameters = "rv-setup-parameters"
    Error = "rv-error"


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
        return ["session_id", "peer_id", "initiate", "public", "private"]


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
            RendezvousProtocolMessageType.ConnectRequest.value:
                ConnectRequest,
            RendezvousProtocolMessageType.SetupParameters.value:
                SetupParameters,
            RendezvousProtocolMessageType.Error.value: Error,
        }

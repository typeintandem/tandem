from tandem.shared.protocol.messages.base import (
    ProtocolMessageBase,
    ProtocolMessageTypeBase,
    ProtocolUtilsBase,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class RendezvousProtocolMessageType(ProtocolMessageTypeBase):
    ConnectRequest = "connect-request"
    SetupParameters = "setup-parameters"


class ConnectRequest(ProtocolMessageBase):
    def __init__(self, **kwargs):
        super(ConnectRequest, self).__init__(
            RendezvousProtocolMessageType.ConnectRequest,
            **kwargs
        )

    @staticvalue
    def _payload_keys(self):
        return ['uuid', 'private_address']


class SetupParameters(ProtocolMessageBase):
    def __init__(self, **kwargs):
        super(SetupParameters, self).__init__(
            RendezvousProtocolMessageType.SetupParameters,
            **kwargs
        )

    @staticvalue
    def _payload_keys(self):
        return ['uuid', 'connect_to']


class RendezvousProtocolUtils(ProtocolUtilsBase):
    @classmethod
    @staticvalue
    def _protocol_message_constructors(cls):
        return {
            RendezvousProtocolMessageType.ConnectRequest.value:
                ConnectRequest,
            RendezvousProtocolMessageType.SetupParameters.value:
                SetupParameters,
        }

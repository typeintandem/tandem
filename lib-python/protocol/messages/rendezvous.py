from tandem.shared.protocol.messages.base import ProtocolMessageBase, ProtocolMessageTypeBase, ProtocolUtilsBase


class RendezvousProtocolMessageType(ProtocolMessageTypeBase):
    ConnectRequest = "connect-request"
    SetupParameters = "setup-parameters"


class ConnectRequest(ProtocolMessageBase):
    def __init__(self, payload):
        super(ConnectRequest, self).__init__(RendezvousProtocolMessageType.ConnectRequest, payload)

    def _payload_keys(self):
        return ['uuid', 'private_address']


class SetupParameters(ProtocolMessageBase):
    def __init__(self, payload):
        super(SetupParameters, self).__init__(RendezvousProtocolMessageType.SetupParameters, payload)

    def _payload_keys(self):
        return ['uuid', 'connect_to']


class RendezvousProtocolUtils(ProtocolUtilsBase):
    @staticmethod
    def deserialize(data):
        message_types = {
            RendezvousProtocolMessageType.ConnectRequest.value: ConnectRequest,
            RendezvousProtocolMessageType.SetupParameters.value: SetupParameters,
        }

        return ProtocolUtilsBase._deserialize(message_types, data)

from tandem.shared.protocol.messages.base import (
    ProtocolMessageTypeBase,
    ProtocolMessageBase,
    ProtocolUtilsBase,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolMessageType(ProtocolMessageTypeBase):
    # Connection setup messages
    Ping = "ia-ping"
    PingBack = "ia-ping-back"
    Syn = "ia-syn"
    Hello = "ia-hello"

    # Regular interagent messages
    NewOperations = "ia-new-operations"
    Bye = "ia-bye"


class Ping(ProtocolMessageBase):
    """
    Sent by the agent to a peer to maintain or open a connection.
    """
    def __init__(self, **kwargs):
        super(Ping, self).__init__(
            InteragentProtocolMessageType.Ping,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["id"]


class PingBack(ProtocolMessageBase):
    """
    Sent in response to a Ping message to acknowledge receipt.
    """
    def __init__(self, **kwargs):
        super(PingBack, self).__init__(
            InteragentProtocolMessageType.PingBack,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["id"]


class Syn(ProtocolMessageBase):
    """
    Sent by the connection initiator to indicate that it has
    completed its connection set up and wishes to begin
    communicating via regular protocol messages.

    The initiator should continue sending this message until
    it receives a regular protocol message from the non-initiator.
    """
    def __init__(self, **kwargs):
        super(Syn, self).__init__(
            InteragentProtocolMessageType.Syn,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return []


class Hello(ProtocolMessageBase):
    """
    Sent directly from one agent to another to introduce itself.

    This message is used to directly establish a connection. It
    is sent after receiving a ConnectTo message from the plugin.

    The should_reply flag is set if the agent wants the remote
    peer to respond with a Hello message containing its ID.
    """
    def __init__(self, **kwargs):
        super(Hello, self).__init__(
            InteragentProtocolMessageType.Hello,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ["id", "should_reply"]


class Bye(ProtocolMessageBase):
    def __init__(self, **kwargs):
        super(Bye, self).__init__(
            InteragentProtocolMessageType.Bye,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return []


class NewOperations(ProtocolMessageBase):
    """
    Sent to other agents to notify them of new CRDT operations to apply.
    """
    def __init__(self, **kwargs):
        super(NewOperations, self).__init__(
            InteragentProtocolMessageType.NewOperations,
            **kwargs,
        )

    @staticvalue
    def _payload_keys(self):
        return ['operations_list']


class InteragentProtocolUtils(ProtocolUtilsBase):
    @classmethod
    @staticvalue
    def _protocol_message_constructors(cls):
        return {
            InteragentProtocolMessageType.Ping.value: Ping,
            InteragentProtocolMessageType.PingBack.value: PingBack,
            InteragentProtocolMessageType.Syn.value: Syn,
            InteragentProtocolMessageType.Hello.value: Hello,
            InteragentProtocolMessageType.Bye.value: Bye,
            InteragentProtocolMessageType.NewOperations.value: NewOperations,
        }

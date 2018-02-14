from tandem.shared.protocol.messages.base import (
    ProtocolMessageTypeBase,
    ProtocolMessageBase,
    ProtocolUtilsBase,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class InteragentProtocolMessageType(ProtocolMessageTypeBase):
    NewOperations = "new-operations"
    Hello = "hello"
    Bye = "bye"


class Hello(ProtocolMessageBase):
    def __init__(self, **kwargs):
        super(Hello, self).__init__(
            InteragentProtocolMessageType.Hello,
            **kwargs
        )

    @staticvalue
    def _payload_keys(self):
        return []


class Bye(ProtocolMessageBase):
    def __init__(self, **kwargs):
        super(Bye, self).__init__(
            InteragentProtocolMessageType.Bye,
            **kwargs
        )

    @staticvalue
    def _payload_keys(self):
        return []


class NewOperations(ProtocolMessageBase):
    """
    Sent to other agents to notify them of new CRDT operations to apply.

    This message could have multiple fragments if the operations payload
    is too large. If there are multiple fragments, the message will
    contain a sequence number and fragment number.

    All fragments in the same message share the same sequence number. The
    fragment number is used to order the payloads when reassembling the
    message.
    """
    def __init__(self, **kwargs):
        super(NewOperations, self).__init__(
            InteragentProtocolMessageType.NewOperations,
            **kwargs
        )

    @staticvalue
    def _payload_keys(self):
        return ['operations_binary']


class InteragentProtocolUtils(ProtocolUtilsBase):
    @classmethod
    @staticvalue
    def _protocol_message_constructors(cls):
        return {
            InteragentProtocolMessageType.Hello.value: Hello,
            InteragentProtocolMessageType.Bye.value: Bye,
            InteragentProtocolMessageType.NewOperations.value: NewOperations,
        }

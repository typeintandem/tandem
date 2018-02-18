import uuid
from tandem.rendezvous.models.connection import Connection
from tandem.rendezvous.stores.session import SessionStore
from tandem.shared.protocol.handlers.base import ProtocolHandlerBase
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolMessageType,
    RendezvousProtocolUtils,
    SetupParameters,
    SessionCreated,
    Error,
)
from tandem.shared.utils.static_value import static_value as staticvalue


def uuid_valid(self, candidate):
    try:
        uuid.UUID(candidate)
        return True
    except ValueError:
        return False


class AgentRendezvousProtocolHandler(ProtocolHandlerBase):
    @staticvalue
    def _protocol_message_utils(self):
        return RendezvousProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            RendezvousProtocolMessageType.NewSession.value:
                self._handle_new_session,
            RendezvousProtocolMessageType.ConnectRequest.value:
                self._handle_connect_request,
        }

    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def _handle_new_session(self, message, sender_address):
        host_id = message.host_id
        if not uuid_valid(host_id):
            self._send_error_message(sender_address, "Invalid host id.")
            return
        session_id, session = SessionStore.get_instance().new_session()
        new_connection = Connection(sender_address, message.private_address)
        session.add_connection(new_connection)
        self._connection_manager.send_data(
            new_connection.get_public_address(),
            self._protocol_message_utils().serialize(SessionCreated(
                session_id=session_id
            )),
        )

    def _handle_connect_request(self, message, sender_address):
        # Validate request identifiers
        connection_id = message.my_id
        session_id = message.session_id
        if not uuid_valid(connection_id) or not uuid_valid(session_id):
            self._send_error_message(sender_address, "Invalid ids.")
            return

        # Validate and fetch the requested session
        session = SessionStore.get_instance().get_session(session_id)
        if session is None:
            self._send_error_message(sender_address, "Invalid session.")
            return

        # Make sure the agent requesting to join is new or has the same
        # "identity" as an agent already in the session.
        initiator = \
            Connection(connection_id, sender_address, message.private_address)
        existing_connection = session.get_connection(connection_id)
        if existing_connection is None:
            session.add_connection(initiator)
        elif not(initiator == existing_connection):
            # Reject the connection request for security reasons, since the
            # client # gets to choose their ID. The first agent to join a
            # session "claims" the ID. This is not foolproof, but it makes
            # it more difficult for someone to join an existing session as
            # someone else.
            self._send_error_message(sender_address, "Invalid session.")
            return

        for member_connection in session.get_connections():
            if not(member_connection == initiator):
                # Send initiator's details to the session member
                self._send_setup_parameters_message(
                    session_id=session_id,
                    recipient=member_connection,
                    should_connect_to=initiator,
                    initiate=False,
                )

                # Send the session member's details to the initiator
                self._send_setup_parameters_message(
                    session_id=session_id,
                    recipient=initiator,
                    should_connect_to=member_connection,
                    initiate=True,
                )

    def _send_setup_parameters_message(
        self,
        session_id,
        recipient,
        should_connect_to,
        initiate,
    ):
        self._connection_manager.send_data(
            recipient.get_public_address(),
            self._protocol_message_utils().serialize(SetupParameters(
                session_id=session_id,
                peer_id=should_connect_to.get_id(),
                initiate=initiate,
                connect_to=[
                    should_connect_to.get_public_address(),
                    should_connect_to.get_private_address(),
                ],
            )),
        )

    def _send_error_message(self, address, message):
        self._connection_manager.send_data(
            address,
            self._protocol_message_utils().serialize(Error(
                message=message,
            )),
        )

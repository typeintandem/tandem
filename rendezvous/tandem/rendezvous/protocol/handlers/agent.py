import uuid
import logging
from tandem.rendezvous.models.connection import Connection
from tandem.rendezvous.stores.session import SessionStore
from tandem.shared.models.peer import Peer
from tandem.shared.protocol.handlers.addressed import AddressedHandler
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolMessageType,
    RendezvousProtocolUtils,
    SetupParameters,
    Error,
)
from tandem.shared.utils.static_value import static_value as staticvalue


def parse_uuid(candidate):
    try:
        return uuid.UUID(candidate)
    except ValueError:
        return None


class AgentRendezvousProtocolHandler(AddressedHandler):
    @staticvalue
    def _protocol_message_utils(self):
        return RendezvousProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            RendezvousProtocolMessageType.ConnectRequest.value:
                self._handle_connect_request,
        }

    def __init__(self, gateway):
        self._gateway = gateway

    def _handle_connect_request(self, message, sender_address):
        # Validate request identifiers
        connection_id = parse_uuid(message.my_id)
        session_id = parse_uuid(message.session_id)
        if connection_id is None or session_id is None:
            logging.info(
                "Rejecting ConnectRequest from {}:{} due to malformed"
                " connection and/or session id."
                .format(*sender_address),
            )
            self._send_error_message(sender_address, "Invalid ids.")
            return

        # Fetch or create the session
        session = SessionStore.get_instance().get_or_create_session(session_id)

        # Make sure the agent requesting to join is new or has the same
        # "identity" as an agent already in the session.
        initiator = Connection(Peer(
            id=connection_id,
            public_address=sender_address,
            private_address=message.private_address,
        ))
        existing_connection = session.get_connection(connection_id)
        if existing_connection is None:
            session.add_connection(initiator)
        elif not(initiator == existing_connection):
            # Reject the connection request for security reasons since the
            # client gets to choose their ID. The first agent to join a
            # session "claims" the ID. This is not foolproof, but it makes
            # it more difficult for someone to join an existing session as
            # someone else.
            logging.info(
                "Rejecting ConnectRequest from {}:{} due to existing"
                " connection with the same id."
                .format(*sender_address),
            )
            self._send_error_message(sender_address, "Invalid session.")
            return

        logging.info(
            "Connection {} is joining session {} requested by {}:{}".format(
                str(connection_id),
                str(session_id),
                *sender_address,
            ),
        )

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
        io_data = self._gateway.generate_io_data(
            self._protocol_message_utils().serialize(SetupParameters(
                session_id=str(session_id),
                peer_id=str(should_connect_to.get_peer().get_id()),
                initiate=initiate,
                public=should_connect_to.get_peer().get_public_address(),
                private=should_connect_to.get_peer().get_private_address(),
            )),
            recipient.get_peer().get_public_address(),
        )
        self._gateway.write_io_data(io_data)

    def _send_error_message(self, address, message):
        io_data = self._gateway.generate_io_data(
            self._protocol_message_utils().serialize(Error(
                message=message,
            )),
            address,
        )
        self._gateway.write_io_data(io_data)

from tandem.rendezvous.models.connection import Connection
from tandem.rendezvous.stores.connection import ConnectionStore
from tandem.rendezvous.stores.session import SessionStore
from tandem.shared.protocol.handler.base import ProtocolHandlerBase
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolMessageType,
    RendezvousProtocolUtils,
    SetupParameters,
)
from tandem.shared.utils.static_value import static_value as staticvalue


class AgentRendezvousProtocolHandler(ProtocolHandlerBase):
    @staticvalue
    def _protocol_message_utils(self):
        return RendezvousProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            RendezvousProtocolMessageType.ConnectRequest.value:
                self._handle_connect_request
        }

    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def _handle_connect_request(self, message, sender_address):
        new_connection = Connection(sender_address, message.private_address)
        session = SessionStore.get_instance().get_session_with_uuid(
            message.uuid
        )

        ConnectionStore.get_instance().register_connection(new_connection)
        session.add_connection(new_connection)

        for connection in session.get_connections():
            if not(connection == new_connection):
                self._connection_manager.send_data(
                    connection,
                    self._protocol_message_utils().serialize(SetupParameters(
                        uuid=message.uuid,
                        connect_to=[(
                            new_connection.get_public_address(),
                            new_connection.get_private_address()
                        )],
                    )),
                )

                self._connection_manager.send_data(
                    new_connection,
                    self._protocol_message_utils().serialize(SetupParameters(
                        uuid=message.uuid,
                        connect_to=[(
                            connection.get_public_address(),
                            connection.get_private_address()
                        )],
                    )),
                )

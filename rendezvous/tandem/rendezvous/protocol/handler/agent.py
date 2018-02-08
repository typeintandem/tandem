from tandem.rendezvous.stores.connection import Connection, ConnectionStore
from tandem.rendezvous.stores.session import SessionStore
from tandem.shared.protocol.handler.base import ProtocolHandlerBase
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolMessageType,
    RendezvousProtocolUtils,
    SetupParameters,
)


class AgentProtocolHandler(ProtocolHandlerBase):
    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def handle_message(self, data, sender_address):
        message_types = {
            RendezvousProtocolMessageType.ConnectRequest.value: self._handle_connect_request,
        }

        return ProtocolHandlerBase.handle_message(RendezvousProtocolUtils, message_types, data, sender_address)

    def _handle_connect_request(self, message, sender_address):
        new_connection = Connection(sender_address, message.private_address)
        session = SessionStore.get_instance().get_session_with_uuid(message.uuid)

        ConnectionStore.get_instance().register_connection(new_connection)
        session.add_connection(new_connection)

        for connection in session.get_connections():
            if not(connection == new_connection):
                self._connection_manager.send_data(
                    connection,
                    RendezvousProtocolUtils.serialize(SetupParameters({
                        "uuid": message.uuid,
                        "connect_to": [(new_connection.get_public_address(), new_connection.get_private_address())],
                    })),
                )

                self._connection_manager.send_data(
                    new_connection,
                    RendezvousProtocolUtils.serialize(SetupParameters({
                        "uuid": message.uuid,
                        "connect_to": [(connection.get_public_address(), connection.get_private_address())],
                    })),
                )

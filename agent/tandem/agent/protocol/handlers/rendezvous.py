import logging
import json
import uuid
from tandem.agent.configuration import USE_RELAY
from tandem.agent.models.connection import HolePunchedConnection
from tandem.agent.stores.connection import ConnectionStore
from tandem.agent.utils.hole_punching import HolePunchingUtils
from tandem.shared.models.peer import Peer
from tandem.shared.protocol.handlers.addressed import AddressedHandler
from tandem.shared.protocol.messages.rendezvous import (
    RendezvousProtocolUtils,
    RendezvousProtocolMessageType,
)
from tandem.agent.protocol.messages.interagent import (
    InteragentProtocolUtils,
    NewOperations,
)
from tandem.shared.utils.static_value import static_value as staticvalue
from tandem.agent.models.connection_state import ConnectionState


class RendezvousProtocolHandler(AddressedHandler):
    @staticvalue
    def _protocol_message_utils(self):
        return RendezvousProtocolUtils

    @staticvalue
    def _protocol_message_handlers(self):
        return {
            RendezvousProtocolMessageType.SetupParameters.value:
                self._handle_setup_parameters,
            RendezvousProtocolMessageType.Error.value:
                self._handle_error,
        }

    def __init__(self, id, gateway, time_scheduler, document):
        self._id = id
        self._gateway = gateway
        self._time_scheduler = time_scheduler
        self._document = document

    def _handle_setup_parameters(self, message, sender_address):
        public_address = (message.public[0], message.public[1])
        private_address = (message.private[0], message.private[1])
        logging.debug(
            "Received SetupParameters - Connect to {} at public {}:{} "
            "and private {}:{}"
            .format(message.peer_id, *public_address, *private_address),
        )
        peer = Peer(
            id=uuid.UUID(message.peer_id),
            public_address=public_address,
            private_address=private_address,
        )
        new_connection = HolePunchedConnection(
            peer=peer,
            initiated_connection=message.initiate,
        )
        new_connection.set_interval_handle(self._time_scheduler.run_every(
            HolePunchingUtils.PING_INTERVAL,
            HolePunchingUtils.generate_send_ping(
                self._gateway,
                peer.get_addresses(),
                self._id,
            ),
        ))

        def handle_hole_punching_timeout(connection):
            if connection.get_connection_state() == ConnectionState.OPEN:
                return

            if not USE_RELAY:
                logging.info(
                    "Connection {} is unreachable. Not switching to RELAY "
                    "because it was disabled."
                    .format(connection.get_peer().get_public_address()),
                )
                connection.set_connection_state(ConnectionState.UNREACHABLE)
                return

            logging.info("Switching connection {} to RELAY".format(
                connection.get_peer().get_public_address()
            ))

            connection.set_connection_state(ConnectionState.RELAY)

            operations = self._document.get_document_operations()
            payload = InteragentProtocolUtils.serialize(NewOperations(
                operations_list=json.dumps(operations)
            ))
            io_data = self._gateway.generate_io_data(
                payload,
                connection.get_peer().get_public_address(),
            )
            self._gateway.write_io_data(
                io_data,
                reliability=True,
            )

        self._time_scheduler.run_after(
            HolePunchingUtils.TIMEOUT,
            handle_hole_punching_timeout,
            new_connection
        )
        ConnectionStore.get_instance().add_connection(new_connection)

    def _handle_error(self, message, sender_address):
        logging.info("Rendezvous Error: {}".format(message.message))

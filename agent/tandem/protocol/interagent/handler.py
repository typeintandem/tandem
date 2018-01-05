import logging
import tandem.protocol.interagent.messages as m


class InteragentProtocolHandler:
    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def handle_message(self, data, sender_address):
        try:
            message = m.deserialize(data)
            if type(message) is m.Ping:
                self._handle_ping(message, sender_address)
        except m.InteragentProtocolMarshalError:
            logging.info("Ignoring invalid interagent protocol message.")
        except:
            logging.exception(
                "Exception when handling interagent protocol message:")
            raise

    def _handle_ping(self, message, sender_address):
        logging.info("Received ping with TTL {}.".format(message.ttl))
        if message.ttl <= 0:
            return
        # Ping the sender back
        sender_connection = \
            self._connection_manager.get_connection(sender_address)
        sender_connection.write_string_message(m.serialize(m.Ping(message.ttl-1)))

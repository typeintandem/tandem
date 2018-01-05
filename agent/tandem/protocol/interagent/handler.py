import logging
import tandem.protocol.interagent.messages as m


class InteragentProtocolHandler:
    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def handle_message(self, data, address):
        try:
            message = m.deserialize(data)
            if type(message) is m.Ping:
                logging.info("Received ping with TTL {}.".format(message.ttl))
                if message.ttl <= 0:
                    return
                # Ping the sender back
                sender_connection = \
                    self._connection_manager.get_connection(address)
                sender_connection.write_string_message(m.serialize(m.Ping(message.ttl-1)))
        except m.EditorProtocolMarshalError:
            pass
        except:
            logging.exception(
                "Exception when handling interagent protocol message:")
            raise

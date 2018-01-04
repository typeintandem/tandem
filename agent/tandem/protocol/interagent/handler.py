import logging
import tandem.protocol.interagent.messages as m


class InteragentProtocolHandler:
    def __init__(self, connection_manager):
        self._connection_manager = connection_manager

    def handle_message(self, message, address):
        try:
            message = m.deserialize(data)
            if type(message) is m.Ping:
                logging.info("Received ping with ttl {}.".format(message.ttl))
        except m.EditorProtocolMarshalError:
            pass
        except:
            logging.exception(
                "Exception when handling interagent protocol message:")
            raise

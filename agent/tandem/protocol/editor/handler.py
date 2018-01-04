import logging
import tandem.protocol.editor.messages as m


class EditorProtocolHandler:
    def __init__(self, std_streams, connection_manager):
        self._std_streams = std_streams
        self._connection_manager = connection_manager

    def handle_message(self, data):
        try:
            message = m.deserialize(data)
            if type(message) is m.ConnectTo:
                # Connect to another agent
                logging.info(
                    "Tandem Agent is attempting to establish a "
                    "connection to {}:{}.".format(message.host, message.port),
                )
                self._connection_manager.connect_to(message.host, message.port)
            else:
                # Echo the message back - placeholder behaviour
                response = m.serialize(message)
                self._std_streams.write(response)
        except m.EditorProtocolMarshalError:
            logging.info("Ignoring invalid message.")
        except:
            logging.exception(
                "Exception when handling editor protocol message:")
            raise

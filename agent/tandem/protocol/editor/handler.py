import logging
import tandem.protocol.editor.messages as em
import tandem.protocol.interagent.messages as im


class EditorProtocolHandler:
    def __init__(self, std_streams, connection_manager):
        self._std_streams = std_streams
        self._connection_manager = connection_manager

    def handle_message(self, data):
        try:
            message = em.deserialize(data)
            if type(message) is em.ConnectTo:
                self._handle_connect_to(message)
            elif type(message) is em.UserChangedEditorText:
                self._handle_user_changed_editor_text(message)
        except em.EditorProtocolMarshalError:
            logging.info("Ignoring invalid editor protocol message.")
        except:
            logging.exception(
                "Exception when handling editor protocol message:")
            raise

    def _handle_connect_to(self, message):
        logging.info(
            "Tandem Agent is attempting to establish a "
            "connection to {}:{}.".format(message.host, message.port),
        )
        self._connection_manager.connect_to(message.host, message.port)
        logging.info(
            "Tandem Agent connected to {}:{}."
            .format(message.host, message.port),
        )

        # Ping the agent (this is for testing)
        address = (message.host, message.port)
        connection = self._connection_manager.get_connection(address)
        ping = im.Ping(2)
        connection.write_string_message(im.serialize(ping))

    def _handle_user_changed_editor_text(self, message):
        text_changed = im.serialize(im.TextChanged(message.contents))
        self._connection_manager.broadcast(text_changed)

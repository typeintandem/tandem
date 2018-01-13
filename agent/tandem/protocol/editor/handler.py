import logging
import tandem.protocol.editor.messages as em
import tandem.protocol.interagent.messages as im


class EditorProtocolHandler:
    def __init__(self, std_streams, connection_manager, document):
        self._std_streams = std_streams
        self._connection_manager = connection_manager
        self._document = document

    def handle_message(self, data):
        try:
            message = em.deserialize(data)
            if type(message) is em.ConnectTo:
                self._handle_connect_to(message)
            elif type(message) is em.UserChangedEditorText:
                self._handle_user_changed_editor_text(message)
            elif type(message) is em.NewPatches:
                self._handle_new_patches(message)
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

    def _handle_user_changed_editor_text(self, message):
        text_changed = im.serialize(im.TextChanged(message.contents))
        self._connection_manager.broadcast(text_changed)

    def _handle_new_patches(self, message):
        nested_operations = [
            self._document.set_text_in_range(
                patch["start"],
                patch["end"],
                patch["text"],
            )
            for patch in message.patch_list
        ]
        operations = []
        for operations_list in nested_operations:
            operations.extend(operations_list)
        new_operations_message = im.serialize(im.NewOperations(operations))
        self._connection_manager.broadcast(new_operations_message)

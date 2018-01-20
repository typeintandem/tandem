import os
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
            elif type(message) is em.WriteRequestAck:
                self._handle_write_request_ack(message)
            elif type(message) is em.UserChangedEditorText:
                self._handle_user_changed_editor_text(message)
            elif type(message) is em.NewPatches:
                self._handle_new_patches(message)
            elif type(message) is em.CheckDocumentSync:
                self._handle_check_document_sync(message)
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

    def _handle_write_request_ack(self, message):
        logging.info("Received ACK for seq: {}".format(message.seq))
        text_patches = self._document.apply_queued_operations()
        self._document.set_write_request_sent(False)
        # Even if no text patches need to be applied, we need to reply to
        # the plugin to allow it to accept changes from the user again
        text_patches_message = em.ApplyPatches(text_patches)
        self._std_streams.write_string_message(em.serialize(text_patches_message))
        logging.info("Sent apply patches message for seq: {}".format(message.seq))

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

    def _handle_check_document_sync(self, message):
        document_text_content = self._document.get_document_text()

        # TODO: ignore all other messages until we receive an ack
        contents = os.linesep.join(message.contents) + os.linesep

        if (contents != document_text_content):
            document_lines = document_text_content.split(os.linesep)
            apply_text = em.serialize(em.ApplyText(document_lines))
            self._std_streams.write_string_message(apply_text)

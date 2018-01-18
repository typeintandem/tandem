import logging
import tandem.protocol.editor.messages as em
import tandem.protocol.interagent.messages as im


class InteragentProtocolHandler:
    def __init__(self, std_streams, connection_manager, document):
        self._std_streams = std_streams
        self._connection_manager = connection_manager
        self._document = document

    def handle_new_connection(self, socket, address):
        self._connection_manager.register_connection(socket, address)

        # Send newly connected agent a copy of the document
        operations = self._document.get_document_operations()
        if len(operations) == 0:
            return
        new_operations_message = im.NewOperations(operations)
        new_connection = self._connection_manager.get_connection(address)
        new_connection.write_string_message(
            im.serialize(new_operations_message),
        )

    def handle_message(self, data, sender_address):
        try:
            message = im.deserialize(data)
            if type(message) is im.Ping:
                self._handle_ping(message, sender_address)
            elif type(message) is im.TextChanged:
                self._handle_text_changed(message, sender_address)
            elif type(message) is im.NewOperations:
                self._handle_new_operations(message, sender_address)
        except im.InteragentProtocolMarshalError:
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
        sender_connection.write_string_message(
            im.serialize(im.Ping(message.ttl-1)),
        )

    def _handle_text_changed(self, message, sender_address):
        # Tell the plugin to change the editor's text buffer
        apply_text = em.serialize(em.ApplyText(message.contents))
        self._std_streams.write_string_message(apply_text)

    def _handle_new_operations(self, message, sender_address):
        text_patches = self._document.apply_operations(message.operations_list)
        logging.info("listener: " + self._document.get_document_text())
        if len(text_patches) == 0:
            return
        apply_patches_message = em.ApplyPatches(text_patches)
        self._std_streams.write_string_message(
            em.serialize(apply_patches_message),
        )

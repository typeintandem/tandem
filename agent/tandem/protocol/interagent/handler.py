import logging
import json
import tandem.protocol.editor.messages as em
import tandem.protocol.interagent.messages as im


class InteragentProtocolHandler:
    def __init__(self, std_streams, peer_manager, document):
        self._std_streams = std_streams
        self._peer_manager = peer_manager
        self._document = document
        self._next_editor_sequence = 0

    def handle_message(self, raw_data, sender_address):
        try:
            message = im.deserialize(raw_data)
            if type(message) is im.Hello:
                self._handle_hello(message, sender_address)
            elif type(message) is im.Bye:
                self._handle_bye(message, sender_address)
            elif type(message) is im.NewOperations:
                self._handle_new_operations(message, sender_address)
            else:
                logging.debug("Received unknown interagent message.")
        except im.InteragentProtocolMarshalError:
            logging.info("Ignoring invalid interagent protocol message.")
        except:
            logging.exception(
                "Exception when handling interagent protocol message:")
            raise

    def _handle_hello(self, message, sender_address):
        self._peer_manager.register_peer(sender_address)

        # Send newly connected agent a copy of the document
        operations = self._document.get_document_operations()
        if len(operations) == 0:
            return
        self._peer_manager.send_operations_list(operations, sender_address)

    def _handle_bye(self, message, sender_address):
        self._peer_manager.remove_peer(sender_address)

    def _handle_new_operations(self, message, sender_address):
        if not message.is_fragmented():
            return self._handle_assembled_operations(message.operations_binary)

        peer = self._peer_manager.get_peer(sender_address)
        operations_binary = peer.integrate_new_operations_message(message)

        if operations_binary is not None:
            self._handle_assembled_operations(operations_binary)

    def _handle_assembled_operations(self, operations_binary):
        operations_list = json.loads(operations_binary.decode("utf-8"))
        self._document.enqueue_remote_operations(operations_list)
        if not self._document.write_request_sent():
            self._std_streams.write_string_message(
                em.serialize(em.WriteRequest(self._next_editor_sequence)),
            )
            self._document.set_write_request_sent(True)
            logging.debug(
                "Sent write request seq: {}"
                .format(self._next_editor_sequence),
            )
            self._next_editor_sequence += 1

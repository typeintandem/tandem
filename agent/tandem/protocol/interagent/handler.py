import logging
import tandem.protocol.editor.messages as em
import tandem.protocol.interagent.messages as im


class InteragentProtocolHandler:
    def __init__(self, std_streams, gateway, document):
        self._std_streams = std_streams
        self._gateway = gateway
        self._document = document
        self._next_editor_sequence = 0

    def handle_message(self, raw_data, sender_address):
        try:
            message = im.deserialize(raw_data)
            if type(message) is im.NewOperations:
                self._handle_new_operations(message, sender_address)
            else:
                logging.debug("Received unknown interagent message.")
        except im.InteragentProtocolMarshalError:
            logging.info("Ignoring invalid interagent protocol message.")
        except:
            logging.exception(
                "Exception when handling interagent protocol message:")
            raise

    def _handle_new_operations(self, message, sender_address):
        self._document.enqueue_remote_operations(message.operations_list)
        if not self._document.write_request_sent():
            self._std_streams.write_string_message(
                em.serialize(em.WriteRequest(self._next_editor_sequence)),
            )
            self._document.set_write_request_sent(True)
            logging.debug("Sent write request seq: {}".format(self._next_editor_sequence))
            self._next_editor_sequence += 1

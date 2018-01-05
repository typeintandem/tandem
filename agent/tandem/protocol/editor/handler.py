import logging
import tandem.protocol.editor.messages as m


class EditorProtocolHandler:
    def __init__(self, std_streams):
        self._std_streams = std_streams

    def handle_message(self, data):
        try:
            message = m.deserialize(data)
            response = m.serialize(message)
            self._std_streams.write(response)
        except m.EditorProtocolMarshalError:
            pass
        except:
            logging.exception(
                "Exception when handling editor protocol message:")
            raise

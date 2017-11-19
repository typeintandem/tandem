import traceback
import tandem.protocol.editor.messages as m

class EditorProtocolHandler:
    def __init__(self, std_streams):
        self._std_streams = std_streams
        pass

    def handle_message(self, data):
        # Handle message by echoing
        try:
            message = m.deserialize(data)
            response = m.serialize(message)
            self._std_streams.write(response)
        except m.EditorProtocolMarshalError:
            pass
        except:
            traceback.print_exc()

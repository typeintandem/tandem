class EditorProtocolHandler:
    def __init__(self, std_streams):
        self._std_streams = std_streams
        pass

    # Handle request by echoing
    def handle(self, data):
        self._std_streams.write(data + "\n")

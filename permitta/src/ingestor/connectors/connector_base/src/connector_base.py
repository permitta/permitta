from abc import abstractmethod


class ConnectorBase:
    def __init__(self):
        pass

    @abstractmethod
    def ingest(self):
        pass

from abc import abstractmethod


class ConnectorBase:
    def __init__(self):
        """
        Supports data ingestion for principals, tags and objects
        Each ingestion type maps to a specific model class / table

        A connector typically uses a client to retrieve data
        then passes it to a repository class which writes it into
        a staging table (creates staging table?)

        When the ingestion into the staging table is complete,
        the ingestor should run some DQ checks on this staging table

        Following successful DQ check, a method is called on the repository
        which executes a merge into the target table

        Possibly this will then create a hook which updates the bundle
        """
        pass

    @abstractmethod
    def ingest(self):
        pass

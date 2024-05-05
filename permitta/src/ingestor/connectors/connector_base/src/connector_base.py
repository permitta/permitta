from app_logger import Logger, get_logger
from ingestor.models import PrincipalAttributeDio, PrincipalDio

logger: Logger = get_logger("ingestor.connectors.base")


class ConnectorBase:
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

    def __init__(self):
        self.errors: list[str] = []

    def _log_error(self, error: str) -> None:
        self.errors.append(error)
        logger.error(f"Connector error: {error}")

    def acquire_data(self) -> None:
        pass

    def get_principals(self) -> list[PrincipalDio]:
        logger.info("Skipping ingestion of principals")
        return []

    def get_principal_attributes(self) -> list[PrincipalAttributeDio]:
        logger.info("Skipping ingestion of principal attributes")
        return []

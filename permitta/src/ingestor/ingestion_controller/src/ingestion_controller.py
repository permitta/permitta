from app_logger import Logger, get_logger
from database import Database
from ingestor.connectors import ConnectorBase, ConnectorFactory, LdapConnector
from ingestor.models import PrincipalAttributeDio, PrincipalDio
from models import (
    IngestionProcessDbo,
    ObjectTypeEnum,
    PrincipalAttributeStagingDbo,
    PrincipalStagingDbo,
)
from repositories import IngestionProcessRepository, PrincipalRepository

logger: Logger = get_logger("ingestor.controller")


class IngestionController:
    """
    Ingestion controller executes specific ingestion operations from different sources
    It is called by the CLI, probably in a k8s cronjob
    It is responsible for:
    * setting the status of ingestion_process objects
    * maintaining the staging tables
    * creating the ingestion connector classes (e.g ldap / trino)
    * pulling full or partial datasets from source systems into staging tables for:
      * principals
      * principal attributes
      * attribute groups / group attributes
      * data objects (tables & columns)
    * storing the results of ingestion operations, counts, errors etc
    * merging the results with the main tables

    * the ingestion controller will get the DBOs from the relevant connectors, i.e:
      * principals and attributes from LDAP
      * attribute groups from a JSON/YAML file
      * data objects (tables & columns) with attributes from trino

    * this controller should also provide a mutex via the ingestion process table to lock the staging tables
    """

    def ingest(self, connector_name: str, object_types: list[ObjectTypeEnum]) -> None:
        logger.info("Starting ingestion process")

        # TODO create mutex - in ingestion process table?
        database: Database = Database()
        database.connect()

        # create connector
        connector: ConnectorBase = ConnectorFactory.create_by_name(
            connector_name=connector_name
        )

        # load data into connector
        connector.acquire_data()

        # create the process id & truncate staging
        process_id: int = self._initialise_ingestion_process(
            database=database, connector_name=connector_name, object_types=object_types
        )

        # get each object type from the connector and load into staging
        principal_count: int = 0
        principal_attribute_count: int = 0

        with database.Session.begin() as session:
            if ObjectTypeEnum.PRINCIPAL in object_types:
                principal_dios: list[PrincipalDio] = connector.get_principals()
                principal_count: int = self._stage_principals(
                    session=session, principal_dios=principal_dios
                )
                logger.info(
                    f"Retrieved {principal_count} principals under process ID: {process_id}"
                )

            if ObjectTypeEnum.PRINCIPAL_ATTRIBUTE in object_types:
                principal_attribute_dios: list[PrincipalAttributeDio] = (
                    connector.get_principal_attributes()
                )
                principal_attribute_count: int = self._stage_principal_attributes(
                    session=session, principal_attribute_dios=principal_attribute_dios
                )
                logger.info(
                    f"Retrieved {principal_attribute_count} principal attributes under process ID: {process_id}"
                )

            # commit staging tables
            session.commit()
            logger.info(
                f"Committed data to staging tables under process ID: {process_id}"
            )

        # merge into main tables
        with database.Session.begin() as session:
            try:
                logger.info(f"Starting merge process")
                PrincipalRepository.merge_principals_staging(
                    session=session, ingestion_process_id=process_id
                )
                # TODO this should be optional in case its not a full load
                logger.info(f"Starting merge deactivate process")
                PrincipalRepository.merge_deactivate_principals_staging(
                    session=session, ingestion_process_id=process_id
                )
            finally:
                # close ingestion process
                logger.info(
                    f"Completing ingestion process with process ID: {process_id}"
                )
                IngestionProcessRepository.complete_process(
                    session=session, ingestion_process_id=process_id
                )
                session.commit()

    @staticmethod
    def _stage_principals(session, principal_dios: list[PrincipalDio]) -> int:
        principal_stgs: list[PrincipalStagingDbo] = []
        for principal_dio in principal_dios:
            principal_stg: PrincipalStagingDbo = PrincipalStagingDbo()
            principal_stg.source_uid = principal_dio.source_uid
            principal_stg.first_name = principal_dio.first_name
            principal_stg.last_name = principal_dio.last_name
            principal_stg.user_name = principal_dio.user_name
            principal_stg.email = principal_dio.email
            principal_stgs.append(principal_stg)
        session.add_all(principal_stgs)
        # TODO add DQ rules
        return len(principal_stgs)

    @staticmethod
    def _stage_principal_attributes(
        session, principal_attribute_dios: list[PrincipalAttributeDio]
    ) -> int:
        principal_attribute_stgs: list[PrincipalAttributeStagingDbo] = []
        for principal_attribute_dio in principal_attribute_dios:
            principal_attribute_stg: PrincipalAttributeStagingDbo = (
                PrincipalAttributeStagingDbo()
            )
            principal_attribute_stg.source_uid = principal_attribute_dio.source_uid
            principal_attribute_stg.attribute_key = (
                principal_attribute_dio.attribute_key
            )
            principal_attribute_stg.attribute_value = (
                principal_attribute_dio.attribute_value
            )
            principal_attribute_stgs.append(principal_attribute_stg)
        session.add_all(principal_attribute_stgs)
        return len(principal_attribute_stgs)

    @staticmethod
    def _initialise_ingestion_process(
        database: Database, connector_name: str, object_types: list[ObjectTypeEnum]
    ) -> int:
        with database.Session.begin() as session:
            PrincipalRepository.truncate_staging_tables(session=session)

            process_id: int = IngestionProcessRepository.create(
                session=session,
                source=connector_name,
                object_types=object_types,
            )
            session.commit()

        logger.info(
            f"Created ingestion process with id: {process_id} for object types: {object_types}"
        )
        return process_id

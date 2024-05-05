import re

from app_logger import Logger, get_logger
from clients import LdapClient
from ingestor.connectors.connector_base import ConnectorBase
from ingestor.models import PrincipalAttributeDio, PrincipalDio

from .ldap_connector_config import LdapConnectorConfig

logger: Logger = get_logger("ingestor.connectors.ldap_connector")


class LdapConnector(ConnectorBase):
    CONNECTOR_NAME: str = "ldap"
    AD_GROUP_ATTRIBUTE_KEY: str = "ad_group"

    def __init__(self):
        super().__init__()
        self.ldap_users: list[dict] = []
        self.config: LdapConnectorConfig = LdapConnectorConfig.load()
        logger.info("Created LDAP connector")

    def acquire_data(self) -> None:
        ldap_client: LdapClient = LdapClient()
        ldap_client.connect()
        self.ldap_users: list[dict] = ldap_client.list_users(
            user_search_base=self.config.user_search_base,
            user_search_filter=self.config.user_search_filter,
            attributes=self.config.attributes,
        )
        logger.info(f"Retrieved {len(self.ldap_users)} LDAP users from ldap client")

    def get_principals(self) -> list[PrincipalDio]:
        principals: list[PrincipalDio] = []

        for ldap_user in self.ldap_users:
            try:
                principal: PrincipalDio = PrincipalDio(
                    source_uid=ldap_user.get(self.config.attr_user_id)[
                        0
                    ],  # HACK these should not be arrays
                    first_name=ldap_user.get(self.config.attr_first_name)[0],
                    last_name=ldap_user.get(self.config.attr_last_name)[0],
                    user_name=ldap_user.get(self.config.attr_user_name)[0],
                    email=ldap_user.get(self.config.attr_email)[0],
                )
                principals.append(principal)
            except KeyError as e:
                self._log_error(f"Error ingesting LDAP user: {ldap_user}")
        return principals

    def get_principal_attributes(self) -> list[PrincipalAttributeDio]:
        attributes: list[PrincipalAttributeDio] = []

        for ldap_user in self.ldap_users:
            try:
                source_uid: str = ldap_user.get(self.config.attr_user_id)[0]
                group_dns: list[str] = ldap_user.get(self.config.attr_groups)

                for group_dn in group_dns:
                    group_cn: str = re.search(
                        "cn=([a-z_]*),.*", group_dn, re.IGNORECASE
                    ).group(1)

                    attribute: PrincipalAttributeDio = PrincipalAttributeDio(
                        source_uid=source_uid,
                        attribute_key=self.AD_GROUP_ATTRIBUTE_KEY,
                        attribute_value=group_cn,
                    )
                    attributes.append(attribute)
            except KeyError as e:
                self._log_error(f"Error ingesting LDAP user: {ldap_user}")
        return attributes

    # def ingest(self):
    #     ingestion_source: str = "ldap"
    #
    #     # load config
    #     config: LdapConnectorConfig = LdapConnectorConfig.load()
    #
    #     ldap_client: LdapClient = LdapClient()
    #     ldap_client.connect()
    #     ldap_users: list[dict] = ldap_client.list_users(
    #         user_search_base=config.user_search_base,
    #         user_search_filter=config.user_search_filter,
    #         attributes=config.attributes,
    #     )
    #
    #     with self.database.Session.begin() as session:
    #         PrincipalRepository.truncate_staging_tables(session=session)
    #
    #         process_id: int = IngestionProcessRepository.create(
    #             session=session,
    #             source=ingestion_source,
    #             object_types=[ObjectTypeEnum.PRINCIPAL],
    #         )
    #         session.commit()
    #
    #     errors: list[str] = []
    #     principals: list[PrincipalStagingDbo] = []
    #     attributes: list[PrincipalAttributeStagingDbo] = []
    #
    #     with self.database.Session.begin() as session:
    #         for ldap_user in ldap_users:
    #             try:
    #                 principal: PrincipalStagingDbo = PrincipalStagingDbo()
    #                 principal.source_uid = ldap_user.get(config.attr_user_id)[0]
    #                 principal.first_name = ldap_user.get(config.attr_first_name)[0]
    #                 principal.last_name = ldap_user.get(config.attr_last_name)[0]
    #                 principal.user_name = ldap_user.get(config.attr_user_name)[0]
    #                 principal.email = ldap_user.get(config.attr_email)[0]
    #                 principals.append(principal)
    #
    #                 # apply groups as attributes
    #                 group_dns: list[str] = ldap_user.get(config.attr_groups)
    #                 for group_dn in group_dns:
    #                     attribute: PrincipalAttributeStagingDbo = (
    #                         PrincipalAttributeStagingDbo()
    #                     )
    #                     attribute.principal_source_uid = principal.source_uid
    #                     attribute.attribute_key = (
    #                         PrincipalAttributeDbo.AD_GROUP_ATTRIBUTE_KEY
    #                     )
    #
    #                     group_cn: str = re.search(
    #                         "cn=([a-z_]*),.*", group_dn, re.IGNORECASE
    #                     ).group(1)
    #                     attribute.attribute_value = group_cn
    #                     attributes.append(attribute)
    #
    #             except KeyError as e:
    #                 errors.append(f"Error ingesting LDAP user: {ldap_user}")
    #
    #         session.add_all(principals)
    #         session.add_all(attributes)
    #         session.commit()
    #
    #     # TODO wrap this in try catch and write the error to the ing proc table
    #     with self.database.Session.begin() as session:
    #         PrincipalRepository.merge_principals_staging(
    #             session=session, ingestion_process_id=process_id
    #         )
    #         PrincipalRepository.merge_deactivate_principals_staging(
    #             session=session, ingestion_process_id=process_id
    #         )
    #
    #         IngestionProcessRepository.complete_process(
    #             session=session, ingestion_process_id=process_id
    #         )
    #         session.commit()

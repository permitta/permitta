import re

from clients import LdapClient
from database import Database
from ingestor.connectors.connector_base import ConnectorBase
from models import (
    ObjectTypeEnum,
    PrincipalAttributeDbo,
    PrincipalAttributeStagingDbo,
    PrincipalStagingDbo,
)
from repositories import (
    IngestionProcessRepository,
    PrincipalGroupRepository,
    PrincipalRepository,
)

from .ldap_connector_config import LdapConnectorConfig


class LdapConnector(ConnectorBase):

    def ingest(self):
        ingestion_source: str = "ldap"

        # load config
        config: LdapConnectorConfig = LdapConnectorConfig.load()

        ldap_client: LdapClient = LdapClient()
        ldap_client.connect()
        ldap_users: list[dict] = ldap_client.list_users(
            user_search_base=config.user_search_base,
            user_search_filter=config.user_search_filter,
            attributes=config.attributes,
        )

        with self.database.Session.begin() as session:
            PrincipalRepository.truncate_staging_tables(session=session)

            process_id: int = IngestionProcessRepository.create(
                session=session,
                source=ingestion_source,
                object_types=[ObjectTypeEnum.PRINCIPAL],
            )
            session.commit()

        errors: list[str] = []
        principals: list[PrincipalStagingDbo] = []
        attributes: list[PrincipalAttributeStagingDbo] = []

        with self.database.Session.begin() as session:
            for ldap_user in ldap_users:
                try:
                    principal: PrincipalStagingDbo = PrincipalStagingDbo()
                    principal.source_uid = ldap_user.get(config.attr_user_id)[0]
                    principal.first_name = ldap_user.get(config.attr_first_name)[0]
                    principal.last_name = ldap_user.get(config.attr_last_name)[0]
                    principal.user_name = ldap_user.get(config.attr_user_name)[0]
                    principal.email = ldap_user.get(config.attr_email)[0]
                    principals.append(principal)

                    # apply groups as attributes
                    group_dns: list[str] = ldap_user.get(config.attr_groups)
                    for group_dn in group_dns:
                        attribute: PrincipalAttributeStagingDbo = (
                            PrincipalAttributeStagingDbo()
                        )
                        attribute.principal_source_uid = principal.source_uid
                        attribute.attribute_key = (
                            PrincipalAttributeDbo.AD_GROUP_ATTRIBUTE_KEY
                        )

                        group_cn: str = re.search(
                            "cn=([a-z_]*),.*", group_dn, re.IGNORECASE
                        ).group(1)
                        attribute.attribute_value = group_cn
                        attributes.append(attribute)

                except KeyError as e:
                    errors.append(f"Error ingestion LDAP user: {ldap_user}")

            session.add_all(principals)
            session.add_all(attributes)
            session.commit()

        # TODO wrap this in try catch and write the error to the ing proc table
        with self.database.Session.begin() as session:
            PrincipalRepository.merge_principals_staging(
                session=session, ingestion_process_id=process_id
            )
            PrincipalRepository.merge_deactivate_principals_staging(
                session=session, ingestion_process_id=process_id
            )

            IngestionProcessRepository.complete_process(
                session=session, ingestion_process_id=process_id
            )
            session.commit()

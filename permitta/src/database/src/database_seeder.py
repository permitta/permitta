import json
import os
import uuid
from datetime import datetime
from typing import Type

import yaml
from database import BaseModel, Database
from models import (
    ColumnAttributeDbo,
    ColumnDbo,
    DatabaseAttributeDbo,
    DatabaseDbo,
    IngestionProcessDbo,
    PlatformAttributeDbo,
    PlatformDbo,
    PolicyActionDbo,
    PolicyAttributeDbo,
    PolicyDbo,
    PrincipalAttributeDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
    SchemaAttributeDbo,
    SchemaDbo,
    TableAttributeDbo,
    TableDbo,
)

from .database_config import DatabaseConfig


class DatabaseSeeder:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _get_principals() -> list[PrincipalDbo]:
        with open(
            os.path.join(DatabaseConfig.load().seed_data_path, "principals.json")
        ) as json_file:
            mock_users: list[dict] = json.load(json_file)
            principals: list[PrincipalDbo] = []
            group_prop_index = 0

            for mock_user in mock_users:
                principal_dbo: PrincipalDbo = PrincipalDbo()
                principal_dbo.source_uid = str(uuid.uuid4())
                principal_dbo.activated_at = datetime.now()
                principal_dbo.deactivated_at = None
                principal_dbo.first_name = mock_user.get("first_name")
                principal_dbo.last_name = mock_user.get("last_name")
                principal_dbo.user_name = mock_user.get("username")

                # apply groups
                for group in mock_user.get("groups"):
                    principal_attribute_dbo = PrincipalAttributeDbo()
                    principal_attribute_dbo.attribute_key = "ad_group"
                    principal_attribute_dbo.attribute_value = group
                    principal_attribute_dbo.activated_at = datetime.utcnow()
                    principal_dbo.principal_attributes.append(principal_attribute_dbo)

                principals.append(principal_dbo)
            return principals

    @staticmethod
    def _get_groups() -> list:
        with open(
            os.path.join(DatabaseConfig.load().seed_data_path, "principal_groups.json")
        ) as json_file:
            principal_group_mock_data: list[dict] = json.load(json_file).get("groups")
            principal_groups: list[PrincipalGroupDbo] = []
            for principal_group in principal_group_mock_data:
                principal_group_dbo = PrincipalGroupDbo()
                principal_group_dbo.name = principal_group.get("name")
                principal_group_dbo.description = principal_group.get("description", "")
                principal_group_dbo.membership_attribute_key = principal_group.get(
                    "membership_property"
                ).get("key")
                principal_group_dbo.membership_attribute_value = principal_group.get(
                    "membership_property"
                ).get("value")

                for inheriting_property in principal_group.get(
                    "inheriting_properties", []
                ):
                    principal_group_attr_dbo = PrincipalGroupAttributeDbo()
                    principal_group_attr_dbo.attribute_key = inheriting_property.get(
                        "key"
                    )
                    principal_group_attr_dbo.attribute_value = inheriting_property.get(
                        "value"
                    )
                    principal_group_dbo.principal_group_attributes.append(
                        principal_group_attr_dbo
                    )
                principal_groups.append(principal_group_dbo)
        return principal_groups

    # Platforms
    @staticmethod
    def _get_platforms():
        def _get_platform_dbo(mock_data: dict) -> PlatformDbo:
            platform_dbo: PlatformDbo = PlatformDbo()
            platform_dbo.platform_id = mock_data["platform_id"]  # autoincremented
            platform_dbo.platform_name = mock_data["display_name"]
            platform_dbo.platform_type = mock_data["type"]
            return platform_dbo

        with open(
            os.path.join(DatabaseConfig.load().seed_data_path, "platforms.json")
        ) as platforms_file:
            platforms: list[PlatformDbo] = [
                _get_platform_dbo(mock_data) for mock_data in json.load(platforms_file)
            ]
        return platforms

    @staticmethod
    def _get_attributes(
        object_type: Type[BaseModel], raw_attrs: list[dict]
    ) -> list[BaseModel]:
        attributes: list[object_type] = []
        for raw_attr in raw_attrs:
            attribute = object_type()
            attribute.attribute_key = raw_attr["key"]
            attribute.attribute_value = raw_attr["value"]
            attributes.append(attribute)
        return attributes

    # data objects
    @staticmethod
    def _get_data_objects():
        with open(
            os.path.join(DatabaseConfig.load().seed_data_path, "data_objects_hier.json")
        ) as data_objects_file:
            database_dbos: list[DatabaseDbo] = []
            for raw_database in json.load(data_objects_file).get("databases"):
                database_dbo: DatabaseDbo = DatabaseDbo()
                database_dbo.database_name = raw_database.get("name")
                database_dbo.attributes = DatabaseSeeder._get_attributes(
                    DatabaseAttributeDbo, raw_database.get("attributes")
                )
                database_dbo.platform_id = 1
                database_dbos.append(database_dbo)

                for raw_schema in raw_database.get("schemas"):
                    schema_dbo: SchemaDbo = SchemaDbo()
                    schema_dbo.schema_name = raw_schema.get("name")
                    schema_dbo.attributes = DatabaseSeeder._get_attributes(
                        SchemaAttributeDbo, raw_schema.get("attributes")
                    )
                    database_dbo.schemas.append(schema_dbo)

                    for raw_table in raw_schema.get("tables"):
                        table_dbo: TableDbo = TableDbo()
                        table_dbo.table_name = raw_table.get("name")
                        table_dbo.attributes = DatabaseSeeder._get_attributes(
                            TableAttributeDbo, raw_table.get("attributes")
                        )
                        schema_dbo.tables.append(table_dbo)

                        for raw_column in raw_table.get("columns", []):
                            column: ColumnDbo = ColumnDbo()
                            column.column_name = raw_column.get("name")
                            column.mask = raw_column.get("mask")
                            column.attributes = DatabaseSeeder._get_attributes(
                                ColumnAttributeDbo, raw_column.get("attributes")
                            )
                            table_dbo.columns.append(column)

        return database_dbos

    @staticmethod
    def _get_policies():
        with open(
            os.path.join(DatabaseConfig.load().seed_data_path, "policies.yaml")
        ) as policies_file:
            policies_data = yaml.safe_load(policies_file)

        policies: list[PolicyDbo] = []
        for policy_data in policies_data:
            policy: PolicyDbo = PolicyDbo()
            policy.policy_type = policy_data.get("policy_type")
            policy.name = policy_data.get("name")
            policy.author = policy_data.get("author")
            policy.publisher = policy_data.get("publisher", None)
            policy.description = policy_data.get("description")
            policy.record_updated_by = policy.author
            policy.status = policy_data.get("status")

            if policy.policy_type == PolicyDbo.POLICY_TYPE_DSL:
                policy.policy_dsl = policy_data.get("policy_dsl")

            if policy.policy_type == PolicyDbo.POLICY_TYPE_BUILDER:
                if policy_data.get("action_group", "") == "read":
                    for policy_action_name in PolicyActionDbo.ACTIONS_READ:
                        policy_action: PolicyActionDbo = PolicyActionDbo()
                        policy_action.action_name = policy_action_name
                        policy_action.record_updated_by = policy.author
                        policy.policy_actions.append(policy_action)

            for p_attr in policy_data.get("principal_attributes", []):
                attr = PolicyAttributeDbo()
                attr.attribute_key = p_attr.get("key")
                attr.attribute_value = p_attr.get("value")
                attr.type = PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL
                policy.policy_attributes.append(attr)

            for o_attr in policy_data.get("object_attributes", []):
                attr = PolicyAttributeDbo()
                attr.attribute_key = o_attr.get("key")
                attr.attribute_value = o_attr.get("value")
                attr.type = PolicyAttributeDbo.ATTRIBUTE_TYPE_OBJECT
                policy.policy_attributes.append(attr)
            policies.append(policy)

        return policies

    # platforms are not normally ingested so no proc id
    def _ingest_platforms(self):
        with self.db.Session.begin() as session:
            session.add_all(self._get_platforms())
            session.commit()

    def _get_process_id(self, object_type: str) -> int:
        # create the process id
        ingestion_process_dbo: IngestionProcessDbo = IngestionProcessDbo()
        with self.db.Session.begin() as session:
            session.add(ingestion_process_dbo)
            ingestion_process_dbo.source = "Seed"
            ingestion_process_dbo.object_type = object_type
            session.flush()
            ingestion_process_id = ingestion_process_dbo.ingestion_process_id
            session.commit()
        return ingestion_process_id

    def _ingest_objects(self, object_type: str, object_list: list):
        ingestion_process_id = self._get_process_id(object_type)

        for obj in object_list:
            obj.ingestion_process_id = ingestion_process_id

        with self.db.Session.begin() as session:
            session.add_all(object_list)
            ingestion_process_dbo = session.get(
                IngestionProcessDbo, ingestion_process_id
            )
            ingestion_process_dbo.completed_at = datetime.utcnow()
            ingestion_process_dbo.status = "completed"
            session.commit()

    def seed(self):
        self._ingest_platforms()
        self._ingest_objects("Data Object", self._get_data_objects())
        self._ingest_objects("Principal", self._get_principals())
        self._ingest_objects("Principal Groups", self._get_groups())
        self._ingest_objects("Policies", self._get_policies())

import json
import os
import random
from datetime import datetime

from database import Database
from models import (
    DataObjectTableAttributeDbo,
    DataObjectTableDbo,
    IngestionProcessDbo,
    PlatformDbo,
    PrincipalAttributeDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
)


class DatabaseSeeder:
    db: Database

    def __init__(self):
        self.db = Database()
        self.db.connect()

    @staticmethod
    def _get_principals() -> list[PrincipalDbo]:
        with open("permitta/mock_data/principals.json") as json_file:
            mock_users: list[dict] = json.load(json_file)
            principals: list[PrincipalDbo] = []
            group_prop_index = 0

            with open("permitta/mock_data/principal_groups.json") as tags_file:
                all_group_props = [
                    g.get("membership_property")
                    for g in json.load(tags_file).get("groups")
                ]

            for mock_user in mock_users:
                principal_dbo: PrincipalDbo = PrincipalDbo()
                principal_dbo.activated_at = datetime.now()
                principal_dbo.deactivated_at = None
                principal_dbo.first_name = mock_user.get("first_name")
                principal_dbo.last_name = mock_user.get("last_name")
                principal_dbo.user_name = (
                    mock_user.get("first_name") + mock_user.get("last_name")
                ).lower()
                principal_dbo.job_title = random.choice([""])

                # apply groups
                group_prop: dict = all_group_props[group_prop_index]
                group_prop_index += 1
                if group_prop_index == len(all_group_props):
                    group_prop_index = 0

                principal_attribute_dbo = PrincipalAttributeDbo()
                principal_attribute_dbo.attribute_key = group_prop["key"]
                principal_attribute_dbo.attribute_value = group_prop["value"]
                principal_attribute_dbo.activated_at = datetime.utcnow()
                principal_dbo.principal_attributes.append(principal_attribute_dbo)

                principals.append(principal_dbo)
            return principals

    @staticmethod
    def _get_groups() -> list:
        with open("permitta/mock_data/principal_groups.json") as json_file:
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
            platform_dbo.platform_display_name = mock_data["display_name"]
            platform_dbo.platform_type = mock_data["type"]
            return platform_dbo

        with open("permitta/mock_data/platforms.json") as platforms_file:
            platforms: list[PlatformDbo] = [
                _get_platform_dbo(mock_data) for mock_data in json.load(platforms_file)
            ]
        return platforms

    # data objects
    @staticmethod
    def _get_data_objects():
        with open("permitta/mock_data/data_objects.json") as data_objects_file:
            data_object_table_dbos: list[DataObjectTableDbo] = []
            for table in json.load(data_objects_file):
                # add source tag
                data_object_table_dbo: DataObjectTableDbo = DataObjectTableDbo()
                data_object_table_dbo.activated_at = datetime.utcnow()
                data_object_table_dbo.platform_id = table["platform_id"]
                data_object_table_dbo.database_name = table.get("database")
                data_object_table_dbo.schema_name = table.get("schema")
                data_object_table_dbo.object_name = table.get("table")
                data_object_table_dbo.search_value = f"{table.get('database')}.{table.get('schema')}.{table.get('table')}"

                # randomly apply tags
                with open("permitta/mock_data/data_tags.json") as tags_file:
                    all_props = json.load(tags_file).get("properties")
                    for i in range(0, 2):
                        prop: dict = random.choice(all_props)
                        data_object_table_attribute_dbo = DataObjectTableAttributeDbo()
                        data_object_table_attribute_dbo.attribute_key = prop["key"]
                        data_object_table_attribute_dbo.attribute_value = prop["value"]
                        data_object_table_attribute_dbo.activated_at = datetime.utcnow()
                        data_object_table_dbo.data_object_table_attributes.append(
                            data_object_table_attribute_dbo
                        )

                data_object_table_dbos.append(data_object_table_dbo)
        return data_object_table_dbos

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
            obj.process_id = ingestion_process_id

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
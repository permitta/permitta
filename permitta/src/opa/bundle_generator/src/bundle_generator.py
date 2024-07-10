import json
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from typing import Tuple

from app_logger import Logger, get_logger
from models import PlatformDbo, PrincipalAttributeDbo
from opa.rego_generator import RegoGenerator
from repositories import DataObjectRepository, PrincipalRepository

from .bundle_generator_config import BundleGeneratorConfig

logger: Logger = get_logger("opa.bundle_generator")


@dataclass
class Bundle:
    @property
    def path(self) -> str:
        return os.path.join(self.directory, self.filename)

    directory: str
    filename: str


class BundleGenerator:
    def __init__(self, session, platform_id: int, bundle_name: str):
        self.session = session
        self.platform_id = platform_id
        self.bundle_name = bundle_name

        config: BundleGeneratorConfig = BundleGeneratorConfig().load()
        self.bundle_directory: str = f"{config.temp_directory}/{uuid.uuid4()}"
        self.data_directory: str = f"{self.bundle_directory}/{bundle_name}"
        self.rego_file_path: str = os.path.join(
            self.bundle_directory, f"{bundle_name}.rego"
        )
        self.data_file_path: str = os.path.join(
            self.bundle_directory, f"{bundle_name}", "data.json"
        )
        self.manifest_file_path: str = os.path.join(self.bundle_directory, ".manifest")

    def __enter__(self) -> Bundle:
        os.makedirs(os.path.join(self.data_directory), exist_ok=True)

        # write the rego file
        rego_file_content: str = RegoGenerator.generate_rego_document(
            session=self.session
        )
        with open(self.rego_file_path, "w") as f:
            f.write(rego_file_content)

        # write the data file
        with open(self.data_file_path, "w") as f:
            f.write(
                json.dumps(
                    BundleGenerator.generate_data_object(
                        session=self.session, platform_id=self.platform_id
                    )
                )
            )

        # write the manifest file to scope the bundle
        with open(self.manifest_file_path, "w") as f:
            f.write(json.dumps({"roots": ["trino", "permitta/trino"]}))

        # build the bundle
        result = subprocess.run(
            ["opa", "build", "-b", "."],  # TODO optimise
            capture_output=True,
            text=True,
            cwd=self.bundle_directory,
        )
        if result.returncode != 0:
            raise ValueError(
                f"OPA bundler failed with exit code {result.returncode}, Output: {result.stdout}, Error: {result.stderr}"
            )

        logger.info(
            f"Generated bundle with output: {result.stdout}  Error: {result.stderr}"
        )
        return Bundle(directory=self.bundle_directory, filename="bundle.tar.gz")

    def __exit__(self, *args):
        shutil.rmtree(self.bundle_directory, ignore_errors=True)

    @staticmethod
    def generate_data_object(session, platform_id: int) -> dict:
        principals: list[dict] = BundleGenerator._generate_principals_in_data_object(
            session=session
        )
        data_objects: list[dict] = (
            BundleGenerator._generate_data_objects_in_data_object(
                session=session, platform_id=platform_id
            )
        )

        return {"data_objects": data_objects, "principals": principals}

    @staticmethod
    def _generate_principals_in_data_object(session) -> list[dict]:
        principal_count, principals = PrincipalRepository.get_all(session=session)
        logger.info(f"Retrieved {principal_count} principals from the DB")

        principals_dict: list[dict] = []
        for principal in principals:
            all_attributes: list[PrincipalAttributeDbo] = (
                principal.principal_attributes
                + [a for a in principal.group_membership_attributes]
            )

            principals_dict.append(
                {
                    "name": principal.user_name,
                    "attributes": [
                        {"key": a.attribute_key, "value": a.attribute_value}
                        for a in all_attributes
                    ],
                }
            )
        return principals_dict

    @staticmethod
    def _generate_data_objects_in_data_object(session, platform_id: int) -> list[dict]:
        platform: PlatformDbo = DataObjectRepository.get_platform_by_id(
            session=session, platform_id=platform_id
        )

        data_objects: list[dict] = []

        for database in platform.databases:
            for schema in database.schemas:
                for table in schema.tables:
                    all_attributes: list = (
                        platform.attributes
                        + database.attributes
                        + schema.attributes
                        + table.attributes
                    )

                    data_object: dict = {
                        "object": {
                            "database": database.database_name,
                            "schema": schema.schema_name,
                            "table": table.table_name,
                        },
                        "attributes": [
                            {"key": a.attribute_key, "value": a.attribute_value}
                            for a in all_attributes
                        ],
                    }

                    # add columns if present
                    if table.columns:
                        data_object["columns"] = [
                            {
                                "name": column.column_name,
                                "mask": column.mask,
                                "attributes": [
                                    {"key": a.attribute_key, "value": a.attribute_value}
                                    for a in column.attributes
                                ],
                            }
                            for column in table.columns
                        ]

                    data_objects.append(data_object)
        return data_objects

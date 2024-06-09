from app_logger import Logger, get_logger
from models import PlatformDbo, PrincipalAttributeDbo
from repositories import DataObjectRepository, PrincipalRepository

logger: Logger = get_logger("opa.bundle_generator")


class BundleGenerator:

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

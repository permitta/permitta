from database import Database
from models import AttributeDto, SchemaDto, TableDto

from ..src.data_object_repository import DataObjectRepository


def test_get_all_unique_attributes(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()

    with database.Session.begin() as session:
        attributes = repo.get_all_unique_attributes(session=session)
        assert len(attributes) == 8

        # check they are all unique
        unique_key_values: list[str] = []
        for attribute in attributes:
            unique_key_values.append(
                f"{attribute.attribute_key}={attribute.attribute_value}"
            )
        assert len(set(unique_key_values)) == len(attributes)

        # with a search term on the key
        attributes = repo.get_all_unique_attributes(session=session, search_term="Sal")
        assert len(attributes) == 3

        # with a search term on the value
        attributes = repo.get_all_unique_attributes(
            session=session, search_term="Restricted"
        )
        assert len(attributes) == 2


def test_get_all_tables_with_search_and_pagination(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
        )
        assert table_count == 10
        assert len(tables) == 10
        assert tables[0] == TableDto(
            platform_id=1,
            platform_name="Trino",
            platform_attributes=[],
            database_id=1,
            database_name="datalake",
            database_attributes=[],
            schema_id=3,
            schema_name="sales",
            schema_attributes=[],
            table_id=10,
            table_name="customer_demographics",
            table_attributes=[
                AttributeDto(attribute_key="Sales", attribute_value="Privacy")
            ],
            child_count=0,
            accessible=None,
        )


def test_get_all_tables_with_search_and_pagination__table_name_search(
    database: Database,
) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
            search_term="employ",
        )
        assert table_count == 2
        assert len(tables) == 2
        assert tables[0] == TableDto(
            platform_id=1,
            platform_name="Trino",
            platform_attributes=[],
            database_id=1,
            database_name="datalake",
            database_attributes=[],
            schema_id=1,
            schema_name="hr",
            schema_attributes=[
                AttributeDto(attribute_key="HR", attribute_value="Commercial")
            ],
            table_id=1,
            table_name="employees",
            table_attributes=[],
            child_count=1,
            accessible=None,
        )


def test_get_all_tables_with_search_and_pagination__table_attr_search(
    database: Database,
) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
            search_term="Privacy",
        )
        assert table_count == 2
        assert len(tables) == 2
        assert tables[0] == TableDto(
            platform_id=1,
            platform_name="Trino",
            platform_attributes=[],
            database_id=1,
            database_name="datalake",
            database_attributes=[],
            schema_id=3,
            schema_name="sales",
            schema_attributes=[],
            table_id=10,
            table_name="customer_demographics",
            table_attributes=[
                AttributeDto(attribute_key="Sales", attribute_value="Privacy")
            ],
            child_count=0,
            accessible=None,
        )


def test_get_all_schemas_with_search_and_pagination(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        count, schemas = repo.get_all_schemas_with_search_and_pagination(
            session=session,
            sort_col_name="schemas.schema_name",
            page_number=0,
            page_size=10,
        )
        assert count == 3
        assert len(schemas) == 3

        assert schemas == [
            SchemaDto(
                platform_id=1,
                platform_name="Trino",
                platform_attributes=[],
                database_id=1,
                database_name="datalake",
                database_attributes=[],
                schema_id=1,
                schema_name="hr",
                schema_attributes=[
                    AttributeDto(attribute_key="HR", attribute_value="Commercial")
                ],
                child_count=2,
                accessible=None,
            ),
            SchemaDto(
                platform_id=1,
                platform_name="Trino",
                platform_attributes=[],
                database_id=1,
                database_name="datalake",
                database_attributes=[],
                schema_id=2,
                schema_name="logistics",
                schema_attributes=[],
                child_count=4,
                accessible=None,
            ),
            SchemaDto(
                platform_id=1,
                platform_name="Trino",
                platform_attributes=[],
                database_id=1,
                database_name="datalake",
                database_attributes=[],
                schema_id=3,
                schema_name="sales",
                schema_attributes=[],
                child_count=4,
                accessible=None,
            ),
        ]

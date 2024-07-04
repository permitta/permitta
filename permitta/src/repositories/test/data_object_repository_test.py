from database import Database
from models import AttributeDto, SchemaDto, TableDto

from ..src.data_object_repository import DataObjectRepository


def test_get_all_unique_attributes(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()

    with database.Session.begin() as session:
        attributes = repo.get_all_unique_attributes(session=session)
        assert len(attributes) == 9

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
        assert len(attributes) == 3


def test_get_all_tables_with_search_and_pagination(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=5,
        )

        assert len(tables) == 4  # HACK this should be 5 but pagination is broke
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
        assert table_count == 11


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
        assert table_count == 2


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

        assert len(tables) == 3
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
        assert table_count == 3


def test_get_all_schemas_with_search_and_pagination(database: Database) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        count, schemas = repo.get_all_schemas_with_search_and_pagination(
            session=session,
            sort_col_name="schemas.schema_name",
            page_number=0,
            page_size=10,
        )

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
                child_count=5,
                accessible=None,
            ),
        ]
        assert count == 3


def test_get_all_tables_with_search_pagination_and_attr_filter__one_attr(
    database: Database,
) -> None:
    """
    How should this work?
    Get all the attributes into a single column
    Apply the same logic as in principals
    join back to tables, and on down the tree
    generate the DTOs

    Or, keeping the current schema:
    select platform_attr.key, platform_attr.value, table_attr.key, table_attr.value from
    from ...
    where
    -- for each row, any column-pair must match for all attrs
    (
        platform_attr = attr_0
        or
        schema_attr = attr_0
        or
        table_attr = attr_0
    )
    and
    (
        platform_attr = attr_1
        or
        schema_attr = attr_1
        or
        table_attr = attr_1
    )


    """

    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
            attributes=[AttributeDto(attribute_key="Sales", attribute_value="Privacy")],
        )

        assert len(tables) == 1
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
        assert table_count == 1


def test_get_all_tables_with_search_pagination_and_attr_filter__no_attrs(
    database: Database,
) -> None:
    """
    An empty set of attributes should not match any tables
    """
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
            attributes=[],
        )

        assert len(tables) == 0
        assert table_count == 0


def test_get_all_tables_with_search_pagination_and_attr_filter__null_attrs(
    database: Database,
) -> None:
    """
    A null attribute list should match all tables
    """
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=20,
            attributes=None,
        )

        assert len(tables) == 11
        assert table_count == 11


def test_get_all_tables_with_search_pagination_and_attr_filter__two_attrs(
    database: Database,
) -> None:
    repo: DataObjectRepository = DataObjectRepository()
    with database.Session.begin() as session:
        table_count, tables = repo.get_all_tables_with_search_and_pagination(
            session=session,
            sort_col_name="tables.table_name",
            page_number=0,
            page_size=10,
            attributes=[
                AttributeDto(attribute_key="Sales", attribute_value="Privacy"),
                AttributeDto(attribute_key="Marketing", attribute_value="Privacy"),
            ],
        )

        assert len(tables) == 1
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
            table_id=11,
            table_name="customer_markets",
            table_attributes=[
                AttributeDto(attribute_key="Sales", attribute_value="Privacy"),
                AttributeDto(attribute_key="Marketing", attribute_value="Privacy"),
            ],
            child_count=1,
            accessible=None,
        )
        assert table_count == 1

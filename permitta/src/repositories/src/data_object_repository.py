from typing import Tuple

from models import (
    AttributeDto,
    ColumnAttributeDbo,
    ColumnDbo,
    DatabaseAttributeDbo,
    DatabaseDbo,
    PlatformAttributeDbo,
    PlatformDbo,
    SchemaAttributeDbo,
    SchemaDbo,
    SchemaDto,
    TableAttributeDbo,
    TableDbo,
    TableDto,
)
from sqlalchemy import CTE, Row, Subquery, and_, func, or_
from sqlalchemy.orm import ColumnProperty, Query

from .repository_base import RepositoryBase


class DataObjectRepository(RepositoryBase):

    @staticmethod
    def get_platform_by_id(session, platform_id: int) -> PlatformDbo:
        platform: PlatformDbo = (
            session.query(PlatformDbo)
            .filter(PlatformDbo.platform_id == platform_id)
            .first()
        )
        return platform

    @staticmethod
    def get_table_by_id(session, table_id: int) -> TableDbo:
        table: TableDbo = (
            session.query(TableDbo).filter(TableDbo.table_id == table_id).first()
        )
        return table

    # @staticmethod
    # def get_table_dto_by_id(session, table_id: int) -> TableDto:
    #     table: TableDbo = (
    #         session.query(TableDbo).filter(TableDbo.table_id == table_id).first()
    #     )
    #     table_dto: TableDto = TableDto(
    #
    #
    #     )
    #     return table

    @staticmethod
    def get_all_unique_attributes(session, search_term: str = "") -> list:
        """
        Returns a list of all the unique attributes that a data object can have
        :param session:
        :return:
        """
        attributes: list = (
            session.query(
                PlatformAttributeDbo.attribute_key,
                PlatformAttributeDbo.attribute_value,
            )
            .union(
                session.query(
                    DatabaseAttributeDbo.attribute_key,
                    DatabaseAttributeDbo.attribute_value,
                )
            )
            .union(
                session.query(
                    SchemaAttributeDbo.attribute_key, SchemaAttributeDbo.attribute_value
                )
            )
            .union(
                session.query(
                    TableAttributeDbo.attribute_key, TableAttributeDbo.attribute_value
                )
            )
            .union(
                session.query(
                    ColumnAttributeDbo.attribute_key, ColumnAttributeDbo.attribute_value
                )
            )
            .distinct()
            .filter(
                or_(
                    PlatformAttributeDbo.attribute_key.ilike(f"%{search_term}%"),
                    PlatformAttributeDbo.attribute_value.ilike(f"%{search_term}%"),
                )
            )
            .order_by(
                PlatformAttributeDbo.attribute_key,
                PlatformAttributeDbo.attribute_value,
            )
            .all()
        )
        return attributes

    @staticmethod
    def get_all_tables_with_search_and_pagination(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
        attributes: list[AttributeDto] = None,
    ) -> Tuple[int, list[TableDto]]:
        search_columns: list[str] = [
            "platforms.platform_name",
            "databases.database_name",
            "schemas.schema_name",
            "tables.table_name",
            "platform_attributes.attribute_key",
            "platform_attributes.attribute_value",
            "database_attributes.attribute_key",
            "database_attributes.attribute_value",
            "schema_attributes.attribute_key",
            "schema_attributes.attribute_value",
            "table_attributes.attribute_key",
            "table_attributes.attribute_value",
        ]

        column_count_subquery = (
            session.query(
                ColumnDbo.table_id,
                func.count(1).label("child_count"),
            )
            .group_by(ColumnDbo.table_id)
            .subquery()
        )

        object_and_attr_query: Query = (
            session.query(
                PlatformDbo,
                DatabaseDbo,
                SchemaDbo,
                TableDbo,
                func.coalesce(column_count_subquery.c.child_count, 0),
            )
            .join(DatabaseDbo, DatabaseDbo.platform_id == PlatformDbo.platform_id)
            .join(SchemaDbo, SchemaDbo.database_id == DatabaseDbo.database_id)
            .join(TableDbo, TableDbo.schema_id == SchemaDbo.schema_id)
            .join(
                PlatformAttributeDbo,
                PlatformAttributeDbo.platform_id == PlatformDbo.platform_id,
                isouter=True,
            )
            .join(
                DatabaseAttributeDbo,
                DatabaseAttributeDbo.database_id == DatabaseDbo.database_id,
                isouter=True,
            )
            .join(
                SchemaAttributeDbo,
                SchemaAttributeDbo.schema_id == SchemaDbo.schema_id,
                isouter=True,
            )
            .join(
                TableAttributeDbo,
                TableAttributeDbo.table_id == TableDbo.table_id,
                isouter=True,
            )
            .join(
                column_count_subquery,
                column_count_subquery.c.table_id == TableDbo.table_id,
                isouter=True,
            )
        )

        # attribute filtering
        """
        Need to get all the attributes in a single column
        then ensure they are distinct
        filter with or(each attribute)
        row number
        count == len(attributes)
        select table id
        join back
        """
        if attributes is not None:
            object_and_attr_cte: CTE = (
                session.query(
                    TableDbo.table_id.label("table_id"),
                    TableAttributeDbo.attribute_key.label("table_attribute_key"),
                    TableAttributeDbo.attribute_value.label("table_attribute_value"),
                    SchemaAttributeDbo.attribute_key.label("schema_attribute_key"),
                    SchemaAttributeDbo.attribute_value.label("schema_attribute_value"),
                    DatabaseAttributeDbo.attribute_key.label("db_attribute_key"),
                    DatabaseAttributeDbo.attribute_value.label("db_attribute_value"),
                    PlatformAttributeDbo.attribute_key.label("platform_attribute_key"),
                    PlatformAttributeDbo.attribute_value.label(
                        "platform_attribute_value"
                    ),
                )
                .join(SchemaDbo, TableDbo.schema_id == SchemaDbo.schema_id)
                .join(DatabaseDbo, SchemaDbo.database_id == DatabaseDbo.database_id)
                .join(PlatformDbo, DatabaseDbo.platform_id == PlatformDbo.platform_id)
                .join(
                    TableAttributeDbo,
                    TableDbo.table_id == TableAttributeDbo.table_id,
                    isouter=True,
                )
                .join(
                    SchemaAttributeDbo,
                    SchemaDbo.schema_id == SchemaAttributeDbo.schema_id,
                    isouter=True,
                )
                .join(
                    DatabaseAttributeDbo,
                    DatabaseDbo.database_id == DatabaseAttributeDbo.database_id,
                    isouter=True,
                )
                .join(
                    PlatformAttributeDbo,
                    PlatformDbo.platform_id == PlatformAttributeDbo.platform_id,
                    isouter=True,
                )
            ).cte(name="object_and_attr_cte")

            row_number_column = func.row_number().over(partition_by=TableDbo.table_id)

            object_and_attr_long: Query = (
                session.query(
                    object_and_attr_cte.c.table_id.label("table_id"),
                    object_and_attr_cte.c.table_attribute_key.label("attribute_key"),
                    object_and_attr_cte.c.table_attribute_value.label(
                        "attribute_value"
                    ),
                )
                .union(
                    session.query(
                        object_and_attr_cte.c.table_id.label("table_id"),
                        object_and_attr_cte.c.schema_attribute_key.label(
                            "attribute_key"
                        ),
                        object_and_attr_cte.c.schema_attribute_value.label(
                            "attribute_value"
                        ),
                    ),
                    session.query(
                        object_and_attr_cte.c.table_id.label("table_id"),
                        object_and_attr_cte.c.db_attribute_key.label("attribute_key"),
                        object_and_attr_cte.c.db_attribute_value.label(
                            "attribute_value"
                        ),
                    ),
                    session.query(
                        object_and_attr_cte.c.table_id.label("table_id"),
                        object_and_attr_cte.c.platform_attribute_key.label(
                            "attribute_key"
                        ),
                        object_and_attr_cte.c.platform_attribute_value.label(
                            "attribute_value"
                        ),
                    ),
                )
                .filter(object_and_attr_cte.c.platform_attribute_key.is_not(None))
                .distinct()
            )

            object_and_attr_long_subquery: Subquery = object_and_attr_long.subquery()
            table_ids_and_attr_counts_subquery: Subquery = (
                session.query(
                    object_and_attr_long_subquery.c.table_id.label("table_id"),
                    func.count(1).label("attribute_count"),
                )
                .group_by(object_and_attr_long_subquery.c.table_id)
                .subquery()
            )

            # check for matches with any of the attributes and row number them
            object_and_attr_long_filtered_subquery: Subquery = (
                object_and_attr_long.filter(
                    or_(
                        *[
                            and_(
                                TableAttributeDbo.attribute_key
                                == attribute.attribute_key,
                                TableAttributeDbo.attribute_value
                                == attribute.attribute_value,
                            )
                            for attribute in attributes
                        ]
                    )
                )
                .add_columns(row_number_column.label("row_number"))
                .subquery()
            )

            # table must have all attrs an no extras
            filtered_table_ids_subquery: Subquery = (
                session.query(
                    object_and_attr_long_filtered_subquery.c.table_id,
                    table_ids_and_attr_counts_subquery.c.attribute_count,
                )
                .join(
                    table_ids_and_attr_counts_subquery,
                    table_ids_and_attr_counts_subquery.c.table_id
                    == object_and_attr_long_filtered_subquery.c.table_id,
                )
                .filter(
                    and_(
                        object_and_attr_long_filtered_subquery.c.row_number
                        == len(attributes),
                        table_ids_and_attr_counts_subquery.c.attribute_count
                        == len(attributes),
                    )
                )
                .subquery()
            )

            # join back to the source table to get the principals
            object_and_attr_query: Query = object_and_attr_query.join(
                filtered_table_ids_subquery,
                TableDbo.table_id == filtered_table_ids_subquery.c.table_id,
            )

        object_and_attr_query = RepositoryBase._get_search_query(
            query=object_and_attr_query,
            search_column_names=search_columns,
            search_term=search_term,
        )
        count: int = (
            session.query(object_and_attr_query.subquery().c.table_id)
            .distinct()
            .count()
        )

        object_and_attr_query = DataObjectRepository._get_sort_query(
            query=object_and_attr_query,
            sort_col_name=sort_col_name,
            sort_ascending=sort_ascending,
        )
        object_and_attr_query: Query = DataObjectRepository._get_pagination_query(
            query=object_and_attr_query, page_number=page_number, page_size=page_size
        )
        results = object_and_attr_query.all()

        # construct table dto
        table_dtos: list[TableDto] = []
        for result in results:
            table_dtos.append(
                TableDto(
                    platform_id=result[0].platform_id,
                    platform_name=result[0].platform_name,
                    platform_attributes=RepositoryBase.get_attribute_dtos(result[0]),
                    database_id=result[1].database_id,
                    database_name=result[1].database_name,
                    database_attributes=RepositoryBase.get_attribute_dtos(result[1]),
                    schema_id=result[2].schema_id,
                    schema_name=result[2].schema_name,
                    schema_attributes=RepositoryBase.get_attribute_dtos(result[2]),
                    table_id=result[3].table_id,
                    table_name=result[3].table_name,
                    table_attributes=RepositoryBase.get_attribute_dtos(result[3]),
                    child_count=result[4],
                    accessible=None,
                )
            )

        return count, table_dtos

    @staticmethod
    def get_all_schemas_with_search_and_pagination(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[SchemaDto]]:
        search_columns: list[str] = [
            "platforms.platform_name",
            "databases.database_name",
            "schemas.schema_name",
            "platform_attributes.attribute_key",
            "platform_attributes.attribute_value",
            "database_attributes.attribute_key",
            "database_attributes.attribute_value",
            "schema_attributes.attribute_key",
            "schema_attributes.attribute_value",
        ]

        count_subquery = (
            session.query(
                TableDbo.schema_id,
                func.count(1).label("child_count"),
            )
            .group_by(TableDbo.schema_id)
            .subquery()
        )

        query: Query = (
            session.query(
                PlatformDbo,
                DatabaseDbo,
                SchemaDbo,
                func.coalesce(count_subquery.c.child_count, 0),
            )
            .join(DatabaseDbo, DatabaseDbo.platform_id == PlatformDbo.platform_id)
            .join(SchemaDbo, SchemaDbo.database_id == DatabaseDbo.database_id)
            .join(
                PlatformAttributeDbo,
                PlatformAttributeDbo.platform_id == PlatformDbo.platform_id,
                isouter=True,
            )
            .join(
                DatabaseAttributeDbo,
                DatabaseAttributeDbo.database_id == DatabaseDbo.database_id,
                isouter=True,
            )
            .join(
                SchemaAttributeDbo,
                SchemaAttributeDbo.schema_id == SchemaDbo.schema_id,
                isouter=True,
            )
            .join(
                count_subquery,
                count_subquery.c.schema_id == SchemaDbo.schema_id,
                isouter=True,
            )
        )

        query = RepositoryBase._get_search_query(
            query=query,
            search_column_names=search_columns,
            search_term=search_term,
        )
        count: int = query.count()

        query = DataObjectRepository._get_sort_query(
            query=query,
            sort_col_name=sort_col_name,
            sort_ascending=sort_ascending,
        )
        query: Query = DataObjectRepository._get_pagination_query(
            query=query, page_number=page_number, page_size=page_size
        )
        results = query.all()

        # construct table dto
        schema_dtos: list[SchemaDto] = []
        for result in results:
            schema_dtos.append(
                SchemaDto(
                    platform_id=result[0].platform_id,
                    platform_name=result[0].platform_name,
                    platform_attributes=RepositoryBase.get_attribute_dtos(result[0]),
                    database_id=result[1].database_id,
                    database_name=result[1].database_name,
                    database_attributes=RepositoryBase.get_attribute_dtos(result[1]),
                    schema_id=result[2].schema_id,
                    schema_name=result[2].schema_name,
                    schema_attributes=RepositoryBase.get_attribute_dtos(result[2]),
                    child_count=result[3],
                    accessible=None,
                )
            )

        return count, schema_dtos

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
    TableAttributeDbo,
    TableDbo,
    TableDto,
)
from sqlalchemy import Row, and_, func, or_
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

        count_subquery = (
            session.query(
                ColumnDbo.table_id,
                func.count(1).label("column_count"),
            )
            .group_by(ColumnDbo.table_id)
            .subquery()
        )

        query: Query = (
            session.query(
                PlatformDbo,
                DatabaseDbo,
                SchemaDbo,
                TableDbo,
                func.coalesce(count_subquery.c.column_count, 0),
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
                count_subquery,
                count_subquery.c.table_id == TableDbo.table_id,
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

        def _get_attribute_dtos(
            model: PlatformDbo | DatabaseDbo | SchemaDbo | TableDbo,
        ) -> list[AttributeDto]:
            return [
                AttributeDto(
                    attribute_key=a.attribute_key, attribute_value=a.attribute_value
                )
                for a in model.attributes
            ]

        # construct table dto
        table_dtos: list[TableDto] = []
        for result in results:
            table_dtos.append(
                TableDto(
                    platform_id=result[0].platform_id,
                    platform_name=result[0].platform_name,
                    platform_attributes=_get_attribute_dtos(result[0]),
                    database_id=result[1].database_id,
                    database_name=result[1].database_name,
                    database_attributes=_get_attribute_dtos(result[1]),
                    schema_id=result[2].schema_id,
                    schema_name=result[2].schema_name,
                    schema_attributes=_get_attribute_dtos(result[2]),
                    table_id=result[3].table_id,
                    table_name=result[3].table_name,
                    table_attributes=_get_attribute_dtos(result[3]),
                    column_count=result[4],
                )
            )

        return count, table_dtos

from typing import Tuple
from repositories import DataObjectRepository
from app_logger import Logger, get_logger
from models import TableDto
from opa import OpaClient

logger: Logger = get_logger("controller.data_objects")


class DataObjectsController:
    @staticmethod
    def get_data_objects_paginated_with_access(
        session,
        logged_in_user: str,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        search_term: str,
    ) -> Tuple[int, list[TableDto]]:
        table_count, tables = (
            DataObjectRepository.get_all_tables_with_search_and_pagination(
                session=session,
                sort_col_name=sort_col_name,
                page_number=page_number,
                page_size=page_size,
                search_term=search_term,
            )
        )

        opa_client: OpaClient = OpaClient()
        table: TableDto
        for table in tables:
            try:
                table.accessible = opa_client.authorise_table(
                    username=logged_in_user,
                    database=table.database_name,
                    schema=table.schema_name,
                    table=table.table_name,
                )
            except Exception as e:
                logger.exception(
                    f"Failed to get accessibility for {logged_in_user} on {table.f_q_table_name}"
                )

        return table_count, tables

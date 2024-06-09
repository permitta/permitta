from datetime import datetime
from typing import Tuple

from models import DecisionLogDbo
from sqlalchemy import Row, and_, or_

from .repository_base import RepositoryBase


class DecisionLogRepository(RepositoryBase):

    @staticmethod
    def get_all_with_search_and_pagination(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[DecisionLogDbo]]:
        return RepositoryBase._get_all_with_search_and_pagination(
            model=DecisionLogDbo,
            session=session,
            sort_col_name=sort_col_name,
            page_number=page_number,
            page_size=page_size,
            sort_ascending=sort_ascending,
            search_term=search_term,
            search_column_names=[
                "username",
                "operation",
                "database",
                "schema",
                "table",
                "column",
            ],
        )

    @staticmethod
    def create_bulk(session, decision_logs: list[dict]):
        decision_log_dbos: list[DecisionLogDbo] = []
        for decision_log in decision_logs:
            decision_log_dbos.append(
                DecisionLogRepository.create(decision_log=decision_log)
            )
        session.add_all(decision_log_dbos)

    @staticmethod
    def create(decision_log: dict) -> DecisionLogDbo:
        _input: dict = decision_log.get("input", {})
        action: dict = _input.get("action", {})
        context: dict = _input.get("context", {})
        resource: dict = action.get("resource", {})

        decision_log_dbo = DecisionLogDbo()
        decision_log_dbo.decision_log_id = decision_log.get("decision_id")
        decision_log_dbo.path = decision_log.get("path", "")
        decision_log_dbo.operation = action.get("operation", "")
        decision_log_dbo.username = context.get("identity", {}).get("user", "")
        decision_log_dbo.timestamp = datetime.fromisoformat(
            decision_log.get("timestamp")
        )

        if decision_log_dbo.operation in [
            "GetColumnMask",
            "SelectFromColumns",
            "FilterTables",
            "FilterColumns",
            "FilterSchemas",
        ]:
            data_object: dict = (
                resource.get("column", {})
                | resource.get("table", {})
                | resource.get("schema", {})
            )
            decision_log_dbo.database = data_object.get("catalogName", "")
            decision_log_dbo.schema = data_object.get("schemaName", "")
            decision_log_dbo.table = data_object.get("tableName", "")
            decision_log_dbo.column = data_object.get("columnName", None) or ", ".join(
                data_object.get("columns", [])
            )
        elif decision_log_dbo.operation in ["AccessCatalog", "FilterCatalogs"]:
            decision_log_dbo.database = resource.get("catalog", {}).get("name", "")

        # result can be an object or a bool
        if isinstance(decision_log.get("result", False), bool):
            decision_log_dbo.permitted = decision_log.get("result", None)
        else:
            decision_log_dbo.expression = decision_log.get("result", {}).get(
                "expression", ""
            )
        return decision_log_dbo

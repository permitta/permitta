from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from flask_pydantic import validate
from models import PlatformDbo, TableDbo
from repositories import DataObjectRepository
from views.models import TableQueryDto

bp = Blueprint("data_objects", __name__, url_prefix="/data-objects")

DEFAULT_SORT_KEY: str = "tables.table_name"


@bp.route("/tables", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryDto = TableQueryDto(sort_key=DEFAULT_SORT_KEY)
    return render_template(
        "partials/data_objects/data-objects-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def tables_table(query: TableQueryDto):
    # if query.sort_key == "platform":
    #     sort_col_name = TableDbo.platform
    # elif query.sort_key == "schema":
    #     sort_col_name = TableDbo.schema_name
    # elif query.sort_key == "object":
    #     sort_col_name = TableDbo.object_name
    # else:
    #     sort_col_name = TableDbo.database_name

    with g.database.Session.begin() as session:
        table_count, tables = (
            DataObjectRepository.get_all_tables_with_search_and_pagination(
                session=session,
                sort_col_name=query.sort_key,
                page_number=query.page_number,
                page_size=query.page_size,
                search_term=query.search_term,
            )
        )
        query.record_count = table_count
        return render_template(
            template_name_or_list="partials/data_objects/data-objects-table.html",
            tables=tables,
            table_count=table_count,
            query_state=query,
        )

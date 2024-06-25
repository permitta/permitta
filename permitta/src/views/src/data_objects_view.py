from extensions import oidc
from flask import (
    Blueprint,
    Response,
    g,
    make_response,
    render_template,
    session as flask_session,
)
from flask_pydantic import validate
from models import TableDbo
from views.models import TableQueryDto
from views.controllers import DataObjectsController

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
    logged_in_user: str = flask_session.get("userinfo", {}).get(
        "preferred_username", ""
    )

    with g.database.Session.begin() as session:
        table_count, tables = (
            DataObjectsController.get_data_objects_paginated_with_access(
                session=session,
                logged_in_user=logged_in_user,
                sort_col_name=query.sort_key,
                page_number=query.page_number,
                page_size=query.page_size,
                search_term=query.search_term,
            )
        )

        query.record_count = table_count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/data_objects/data-objects-table.html",
                tables=tables,
                table_count=table_count,
                query_state=query,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/table-detail-modal/<table_id>", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def table_detail_modal(table_id: int):
    with g.database.Session.begin() as session:
        table: TableDbo = DataObjectRepository.get_table_by_id(
            session=session, table_id=table_id
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/data_objects/table-detail-modal.html",
                table=table,
            )
        )
        return response

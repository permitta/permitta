from extensions import oidc
from flask import Blueprint, Response, g, make_response, render_template
from flask import session as flask_session
from flask_pydantic import validate
from models import TableDbo
from views.controllers import DataObjectsController
from views.models import BreadcrumbsVm, TableQueryVm

bp = Blueprint("data_objects", __name__, url_prefix="/data-objects")

TABLES_SORT_KEY: str = "tables.table_name"
SCHEMAS_SORT_KEY: str = "schemas.schema_name"
SCOPE_TABLES: str = "tables"
SCOPE_SCHEMAS: str = "schemas"


@bp.route("/tables", methods=["GET"])
@oidc.oidc_auth("default")
def index_tables():
    query_state: TableQueryVm = TableQueryVm(
        sort_key=TABLES_SORT_KEY, scope=SCOPE_TABLES
    )
    breadcrumbs: BreadcrumbsVm = BreadcrumbsVm(
        items=["Data Objects", "All Schemas", "Tables"]
    )
    return render_template(
        "partials/data_objects/data-objects-search.html",
        query_state=query_state,
        breadcrumbs=breadcrumbs,
    )


@bp.route("/schemas", methods=["GET"])  # TODO can these be compressed?
@oidc.oidc_auth("default")
def index_schemas():
    query_state: TableQueryVm = TableQueryVm(
        sort_key=SCHEMAS_SORT_KEY, scope=SCOPE_SCHEMAS
    )
    breadcrumbs: BreadcrumbsVm = BreadcrumbsVm(items=["Data Objects", "Schemas"])
    return render_template(
        "partials/data_objects/data-objects-search.html",
        query_state=query_state,
        breadcrumbs=breadcrumbs,
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def table(query: TableQueryVm):
    logged_in_user: str = flask_session.get("userinfo", {}).get(
        "preferred_username", ""
    )

    query_function = (
        DataObjectsController.get_schemas_paginated_with_access
        if query.scope == SCOPE_SCHEMAS
        else DataObjectsController.get_tables_paginated_with_access
    )

    with g.database.Session.begin() as session:
        table_count, tables = query_function(
            session=session,
            logged_in_user=logged_in_user,
            sort_col_name=query.sort_key,
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
            attributes=query.attribute_dtos,
        )

        query.record_count = table_count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/data_objects/data-objects-table.html",
                tables=tables,
                table_count=table_count,
                query_state=query,
                compact=False,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/table-compact", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def table_compact(query: TableQueryVm):
    with g.database.Session.begin() as session:
        table_count, tables = DataObjectsController.get_tables_paginated_with_access(
            session=session,
            logged_in_user=None,
            sort_col_name=query.sort_key,
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
            attributes=query.attribute_dtos,
        )

        query.record_count = table_count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/data_objects/data-objects-table.html",
                tables=tables,
                table_count=table_count,
                query_state=query,
                compact=True,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/table-detail-modal/<table_id>", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def table_detail_modal(table_id: int):
    with g.database.Session.begin() as session:
        table: TableDbo = DataObjectsController.get_table_by_id(
            session=session, table_id=table_id
        )
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/data_objects/table-detail-modal.html",
                table=table,
            )
        )
        return response

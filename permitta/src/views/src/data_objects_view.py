from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from flask_pydantic import validate
from models import DataObjectTableDbo, PlatformDbo
from views.models import TableQueryDto

bp = Blueprint("data_objects", __name__, url_prefix="/data-objects")

DEFAULT_SORT_KEY: str = "database"


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryDto = TableQueryDto(sort_key=DEFAULT_SORT_KEY)
    return render_template(
        "partials/data_objects/data-objects-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def data_objects_table(query: TableQueryDto):
    if query.sort_key == "platform":
        sort_col_name = DataObjectTableDbo.platform
    elif query.sort_key == "schema":
        sort_col_name = DataObjectTableDbo.schema_name
    elif query.sort_key == "object":
        sort_col_name = DataObjectTableDbo.object_name
    else:
        sort_col_name = DataObjectTableDbo.database_name

    with g.database.Session.begin() as session:
        # TODO move this bit to a repository and test it
        db_query = (
            session.query(DataObjectTableDbo)
            .filter(DataObjectTableDbo.search_value.ilike(f"%{query.search_term}%"))
            .order_by(sort_col_name)
        )

        data_objects: list[DataObjectTableDbo] = db_query.all()
        data_object_count: int = db_query.count()
        query.record_count = data_object_count

        return render_template(
            template_name_or_list="partials/data_objects/data-objects-table.html",
            data_objects=data_objects,
            data_object_count=data_object_count,
            query_state=query,
        )

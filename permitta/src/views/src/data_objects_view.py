from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from models import DataObjectTableDbo, PlatformDbo

bp = Blueprint("data_objects", __name__, url_prefix="/data-objects")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def data_objects_table():
    search_term: str = request.args.get("searchTerm", "")
    sort_key: str = request.args.get("sort-key", "")

    if sort_key == "platform":
        order_column = DataObjectTableDbo.database_name
        # order_column = DataObjectTableDbo.platform.platform_display_name
    elif sort_key == "database":
        order_column = DataObjectTableDbo.database_name
    elif sort_key == "schema":
        order_column = DataObjectTableDbo.schema_name
    elif sort_key == "object":
        order_column = DataObjectTableDbo.object_name
    else:
        order_column = DataObjectTableDbo.object_name

    with g.database.Session.begin() as session:
        # TODO move this bit to a repository and test it
        query = (
            session.query(DataObjectTableDbo)
            .filter(DataObjectTableDbo.search_value.ilike(f"%{search_term}%"))
            .order_by(order_column)
        )

        data_objects: list[DataObjectTableDbo] = query.all()
        data_object_count: int = query.count()

        return render_template(
            template_name_or_list="partials/data_objects/data-objects-table.html",
            data_objects=data_objects,
            data_object_count=data_object_count,
        )

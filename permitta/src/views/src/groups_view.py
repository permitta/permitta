from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from models import PrincipalGroupDbo, PrincipalGroupAttributeDbo

bp = Blueprint("groups", __name__, url_prefix="/groups")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def groups_table():
    search_term: str = request.args.get("searchTerm", "")
    sort_key: str = request.args.get("sort-key", "")

    if sort_key == "membership_attribute":
        order_column = PrincipalGroupDbo.membership_attribute_key, PrincipalGroupDbo.membership_attribute_value
    else:
        order_column = PrincipalGroupDbo.name

    with g.database.Session.begin() as session:
        # TODO move this bit to a repository and test it
        query = (
            session.query(PrincipalGroupDbo)
            # .filter(DataObjectTableDbo.search_value.ilike(f"%{search_term}%"))
            .order_by(order_column)
        )

        groups: list[PrincipalGroupDbo] = query.all()
        group_count: int = query.count()


        return render_template(
            template_name_or_list="partials/groups/groups-table.html",
            groups=groups,
            group_count=group_count,
        )

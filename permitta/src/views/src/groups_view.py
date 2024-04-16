from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request, make_response, Response
from models import PrincipalGroupAttributeDbo, PrincipalGroupDbo

bp = Blueprint("groups", __name__, url_prefix="/groups")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    return render_template("partials/groups/groups-search.html")


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
def groups_table():
    search_term: str = request.args.get("searchTerm", "")
    sort_key: str = request.args.get("sort-key", "")

    if sort_key == "membership_attribute":
        order_column = PrincipalGroupDbo.membership_attribute_key
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

        response: Response = make_response(render_template(
            template_name_or_list="partials/groups/groups-table.html",
            groups=groups,
            group_count=group_count,
            sort_key=sort_key,
            search_term=search_term
        ))
        response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
        return response

@bp.route("/detail-modal/<principal_group_id>", methods=["GET"])
@oidc.oidc_auth("default")
def group_detail_modal(principal_group_id):
    with g.database.Session.begin() as session:
        principal_group: PrincipalGroupDbo = (
            session.query(PrincipalGroupDbo)
            .filter(PrincipalGroupDbo.principal_group_id == principal_group_id).first()
        )

        response: Response = make_response(render_template(
            template_name_or_list="partials/groups/group-detail-modal.html",
            principal_group=principal_group,
        ))
        return response

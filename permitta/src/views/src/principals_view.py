from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from models import PrincipalDbo, PrincipalGroupDbo, PrincipalGroupAttributeDbo

bp = Blueprint("principals", __name__, url_prefix="/principals")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    return render_template("partials/principals/principals-search.html")


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
def principals_table():
    search_term: str = request.args.get("searchTerm", "")
    sort_key: str = request.args.get("sortKey", "")

    if sort_key == "principal-name":
        order_column = PrincipalDbo.user_name
    elif sort_key == "job-title":
        order_column = PrincipalDbo.job_title
    else:
        order_column = PrincipalDbo.last_name

    with g.database.Session.begin() as session:
        # TODO move this bit to a repository and test it
        principals: list[Type[PrincipalDbo]] = (
            session.query(PrincipalDbo)
            .filter(PrincipalDbo.user_name.ilike(f"%{search_term}%"))
            .order_by(order_column)
            .limit(20)
            .all()
        )
        principal_count: int = session.query(PrincipalDbo).count()
        # attributes: list = principals

        return render_template(
            template_name_or_list="partials/principals/principals-table.html",
            principals=principals,
            principal_count=principal_count,
        )

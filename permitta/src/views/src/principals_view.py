from typing import Type

from flask import Blueprint, g, render_template, request
from models import PrincipalDbo

bp = Blueprint("principals", __name__, url_prefix="/principals")


@bp.route("/", methods=["GET"])
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

        return render_template(
            template_name_or_list="partials/principals-table.html",
            principals=principals,
            principal_count=principal_count,
        )

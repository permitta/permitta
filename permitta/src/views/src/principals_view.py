from extensions import oidc
from flask import Blueprint, g, render_template, request
from models import PrincipalDbo, PrincipalGroupDbo, PrincipalGroupAttributeDbo
from repositories import PrincipalRepository
from flask_pydantic import validate
from views.models import TableQueryDto


bp = Blueprint("principals", __name__, url_prefix="/principals")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryDto = TableQueryDto(sort_key="user_name")

    return render_template(
        "partials/principals/principals-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def principals_table(query: TableQueryDto):
    with g.database.Session.begin() as session:
        repo: PrincipalRepository = PrincipalRepository()
        principal_count, principals = repo.get_all(
            session=session,
            sort_col_name=query.sort_key,  # TODO is this SQL injection?
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
        )
        query.record_count = principal_count
        return render_template(
            template_name_or_list="partials/principals/principals-table.html",
            principals=principals,
            principal_count=principal_count,
            query_state=query,
        )

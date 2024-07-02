from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import (
    Blueprint,
    Response,
    g,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_pydantic import validate
from models import DecisionLogDbo
from repositories import DecisionLogRepository
from views.models import TableQueryVm

bp = Blueprint("decision_logs", __name__, url_prefix="/decision-logs")

DEFAULT_SORT_KEY: str = "timestamp"


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryVm = TableQueryVm(sort_key=DEFAULT_SORT_KEY)
    return render_template(
        "partials/decision_logs/decision-logs-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def decision_logs_table(query: TableQueryVm):
    with g.database.Session.begin() as session:
        repo: DecisionLogRepository = DecisionLogRepository()
        count, decision_logs = repo.get_all_with_search_and_pagination(
            session=session,
            sort_col_name=query.sort_key,  # TODO is this SQL injection?
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
            sort_ascending=False,
        )

        query.record_count = count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/decision_logs/decision-logs-table.html",
                decision_logs=decision_logs,
                count=count,
                query_state=query,
            )
        )
        response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
        return response

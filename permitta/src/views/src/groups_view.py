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
from models import PrincipalDbo, PrincipalGroupAttributeDbo, PrincipalGroupDbo
from pydantic import BaseModel
from repositories import PrincipalGroupRepository, PrincipalRepository
from views.models import TableQueryDto

bp = Blueprint("groups", __name__, url_prefix="/groups")

DEFAULT_SORT_KEY: str = "name"


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryDto = TableQueryDto(sort_key=DEFAULT_SORT_KEY)
    return render_template(
        "partials/groups/groups-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def groups_table(query: TableQueryDto):
    with g.database.Session.begin() as session:
        repo: PrincipalGroupRepository = PrincipalGroupRepository()
        group_count, groups = repo.get_all(
            session=session,
            sort_col_name=query.sort_key,  # TODO is this SQL injection?
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
        )

        query.record_count = group_count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/groups/groups-table.html",
                groups=groups,
                group_count=group_count,
                query_state=query,
            )
        )
        response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
        return response


@bp.route("/detail-modal/<principal_group_id>", methods=["GET"])
@oidc.oidc_auth("default")
def group_detail_modal(principal_group_id: str):
    with g.database.Session.begin() as session:
        principal_group: PrincipalGroupDbo = (
            session.query(PrincipalGroupDbo)
            .filter(PrincipalGroupDbo.principal_group_id == int(principal_group_id))
            .first()
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/groups/group-detail-modal.html",
                principal_group=principal_group,
            )
        )
        return response


@bp.route("/members-modal/<principal_group_id>", methods=["GET"])
@oidc.oidc_auth("default")
def group_members_modal(principal_group_id: str):
    with g.database.Session.begin() as session:
        repo: PrincipalGroupRepository = PrincipalGroupRepository()
        principal_count, principals = repo.get_principal_group_members(
            session=session, principal_group_id=int(principal_group_id)
        )
        group_name, group_description = (
            session.query(PrincipalGroupDbo.name, PrincipalGroupDbo.description)
            .filter(PrincipalGroupDbo.principal_group_id == int(principal_group_id))
            .first()
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/groups/group-members-modal.html",
                principals=principals,
                principal_count=principal_count,
                group_name=group_name,
                group_description=group_description,
            )
        )
        return response


@bp.route("/edit-modal/<principal_group_id>", methods=["GET"])
@oidc.oidc_auth("default")
def group_edit_modal(principal_group_id: str):
    with g.database.Session.begin() as session:
        principal_group: (
            PrincipalGroupDbo
        ) = PrincipalGroupRepository().get_principal_group_by_id(
            session=session, principal_group_id=int(principal_group_id)
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/groups/group-edit-modal.html",
                principal_group=principal_group,
            )
        )
        return response


class PrincipalGroupDto(BaseModel):
    principal_group_id: int
    name: str
    description: str
    membership_attribute_key: str
    membership_attribute_value: str


@bp.route("/", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def group_put(form: PrincipalGroupDto):
    with g.database.Session.begin() as session:
        principal_group: (
            PrincipalGroupDbo
        ) = PrincipalGroupRepository().get_principal_group_by_id(
            session=session, principal_group_id=form.principal_group_id
        )
        principal_group.name = form.name
        principal_group.description = form.description
        principal_group.membership_attribute_key = form.membership_attribute_key
        principal_group.membership_attribute_value = form.membership_attribute_value
        session.commit()

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/groups/group-edit-modal.html",
                principal_group=form,
            ),
        )
        response.headers.set("HX-Trigger-After-Swap", "groups-table-updated")
        return response

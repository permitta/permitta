from dataclasses import dataclass
from typing import Type
from pydantic import BaseModel
from flask_pydantic import validate

from extensions import oidc
from flask import (
    Blueprint,
    g,
    render_template,
    request,
    make_response,
    Response,
    redirect,
    url_for,
)
from models import PrincipalGroupAttributeDbo, PrincipalGroupDbo, PrincipalDbo
from repositories import PrincipalRepository, PrincipalGroupRepository

from views.models import TableQueryDto

bp = Blueprint("groups", __name__, url_prefix="/groups")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryDto = TableQueryDto(
        sort_key="name"
    )
    return render_template(
        "partials/groups/groups-search.html", query_state=query_state
    )


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def groups_table(query: TableQueryDto):
    if query.sort_key == "membership_attribute":
        sort_col_name = PrincipalGroupDbo.membership_attribute_key
    else:
        sort_col_name = PrincipalGroupDbo.name

    with g.database.Session.begin() as session:
        # TODO move this bit to a repository and test it
        query = (
            session.query(PrincipalGroupDbo)
            # .filter(DataObjectTableDbo.search_value.ilike(f"%{search_term}%"))
            .order_by(sort_col_name)
        )

        groups: list[PrincipalGroupDbo] = query.all()
        group_count: int = query.count()

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
def group_detail_modal(principal_group_id):
    with g.database.Session.begin() as session:
        principal_group: PrincipalGroupDbo = (
            session.query(PrincipalGroupDbo)
            .filter(PrincipalGroupDbo.principal_group_id == principal_group_id)
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
def group_members_modal(principal_group_id):
    with g.database.Session.begin() as session:
        repo: PrincipalRepository = PrincipalRepository()
        principal_count, principals = repo.get_principal_group_members(
            session=session, principal_group_id=principal_group_id
        )
        group_name, group_description = (
            session.query(PrincipalGroupDbo.name, PrincipalGroupDbo.description)
            .filter(PrincipalGroupDbo.principal_group_id == principal_group_id)
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
def group_edit_modal(principal_group_id):
    with g.database.Session.begin() as session:
        principal_group: (
            PrincipalGroupDbo
        ) = PrincipalGroupRepository().get_principal_group_by_id(
            session=session, principal_group_id=principal_group_id
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

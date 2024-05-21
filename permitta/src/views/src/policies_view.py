from dataclasses import dataclass
from typing import Type

from app_logger import Logger, get_logger
from extensions import oidc
from flask import Blueprint, Response, abort, g, make_response, render_template, request
from flask_pydantic import validate
from models import (
    AttributeDto,
    DataObjectTableDbo,
    PlatformDbo,
    PolicyAttributeDbo,
    PolicyDbo,
    PrincipalAttributeDbo,
)
from repositories import DataObjectRepository, PolicyRepository, PrincipalRepository
from views.models import PolicyMetadataDto, TableQueryDto

bp = Blueprint("policies", __name__, url_prefix="/policies")

logger: Logger = get_logger("views.policy")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    return render_template("partials/policies/policies-search.html")


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def policies_table(query: TableQueryDto):
    with g.database.Session.begin() as session:
        policy_count, policies = PolicyRepository.get_all_with_search_and_pagination(
            session=session,
            sort_col_name=query.sort_key,  # TODO is this SQL injection?
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policies/policies-table.html",
                policies=policies,
                policy_count=policy_count,
            )
        )
    return response


@bp.route("/<policy_id>", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_policy(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder.html",
            active_tab="metadata",
            policy=policy,
        )


@bp.route("/<policy_id>/metadata", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_policy_metadata(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
            active_tab="metadata",
            policy=policy,
        )


# @bp.route("/create/metadata", methods=["GET"])
# @oidc.oidc_auth("default")
# def policy_create_metadata():
#     return render_template(
#         template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
#         active_tab="metadata",
#     )


@bp.route("/<policy_id>/metadata", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def update_policy_metadata(policy_id: int, body: PolicyMetadataDto):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        policy.name = body.name
        policy.description = body.description
        session.commit()

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
                active_tab="metadata",
                policy=body,
            )
        )

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


@bp.route("/<policy_id>/principal_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_principal_attributes(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder-principal-attributes.html",
            active_tab="principals",
            policy=policy,
        )


@bp.route("/<policy_id>/object_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_object_attributes(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder-object-attributes.html",
            active_tab="objects",
            policy=policy,
        )


@bp.route("/create/all_principal_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def all_principal_attributes(query: TableQueryDto):
    with g.database.Session.begin() as session:
        principal_attributes: list[AttributeDto] = (
            PrincipalRepository.get_all_unique_attributes(
                session=session, search_term=query.search_term
            )
        )

        return render_template(
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=principal_attributes,
            attribute_id_prefix="principal_attribute",
        )


@bp.route("/create/all_object_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def all_object_attributes(query: TableQueryDto):
    with g.database.Session.begin() as session:
        object_attributes: list[AttributeDto] = (
            DataObjectRepository.get_all_unique_attributes(
                session=session, search_term=query.search_term
            )
        )

        return render_template(
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=object_attributes,
            attribute_id_prefix="object_attribute",
        )

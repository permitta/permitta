from dataclasses import dataclass
from typing import Type

from extensions import oidc
from flask import Blueprint, g, render_template, request
from flask_pydantic import validate
from models import AttributeDto, DataObjectTableDbo, PlatformDbo, PrincipalAttributeDbo
from repositories import PrincipalRepository
from views.models import TableQueryDto

bp = Blueprint("policies", __name__, url_prefix="/policies")


# @bp.route("/", methods=["GET"])
# @oidc.oidc_auth("default")
# def index():
#     return render_template("partials/policies/policies-search.html")


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
def policies_table():
    # search_term: str = request.args.get("searchTerm", "")
    # sort_key: str = request.args.get("sort-key", "")

    # if sort_key == "platform":
    #     order_column = DataObjectTableDbo.database_name
    #     #order_column = DataObjectTableDbo.platform.platform_display_name
    # elif sort_key == "database":
    #     order_column = DataObjectTableDbo.database_name
    # elif sort_key == "schema":
    #     order_column = DataObjectTableDbo.schema_name
    # elif sort_key == "object":
    #     order_column = DataObjectTableDbo.object_name
    # else:
    #     order_column = DataObjectTableDbo.object_name

    # with g.database.Session.begin() as session:
    #     # TODO move this bit to a repository and test it
    #     query = (
    #         session.query(DataObjectTableDbo)
    #         .filter(DataObjectTableDbo.search_value.ilike(f"%{search_term}%"))
    #         .order_by(order_column)
    #     )
    #
    #     data_objects: list[DataObjectTableDbo] = query.all()
    #     data_object_count: int = query.count()
    #
    #     @dataclass
    #     class Dumb:
    #         attribute_key: str
    #         attribute_value: str
    #
    #     for data_object in data_objects:
    #         data_object.data_object_attributes = [
    #             Dumb(attribute_key="Key", attribute_value="Value"),
    #             Dumb(attribute_key=None, attribute_value="Tag")
    #         ]

    @dataclass
    class Attribute:
        attribute_key: str | None
        attribute_value: str

    @dataclass
    class Policy:
        name: str
        description: str
        action: str
        group_operator: str
        operator: str
        principal_attributes: list[Attribute]
        object_attributes: list[Attribute]

    policies: list[Policy] = [
        Policy(
            name="General",
            action="Allow if",
            group_operator="ALL",
            operator="IN",
            principal_attributes=[Attribute(attribute_key=None, attribute_value="*")],
            object_attributes=[Attribute(attribute_key=None, attribute_value="*")],
            description="Principal must possess all attributes assigned to the object",
        ),
        Policy(
            name="Location Restriction",
            action="Deny if",
            group_operator="",
            operator="",
            principal_attributes=[
                Attribute(attribute_key="Work Order", attribute_value="nbn-COMMERCIAL")
            ],
            object_attributes=[
                Attribute(attribute_key="Location", attribute_value="nbn-RESTRICTED")
            ],
            description="A principal with Work Order COMMERCIAL cannot access Location RESTRICTED",
        ),
    ]

    return render_template(
        template_name_or_list="partials/policies/policies-table.html",
        policies=policies,
        policy_count=1,
    )


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def policy_detail():

    # with g.database.Session.begin() as session:
    #     principal_attributes: list[AttributeDto] = (
    #         PrincipalRepository.get_all_unique_attribute_kvs(
    #             session=session, search_term=query.search_term
    #         )
    #     )

    return render_template(
        # template_name_or_list="partials/policies/policy-draggable.html",
        template_name_or_list="partials/policy_builder/policy-builder.html",
        # principal_attributes=principal_attributes,
    )


@bp.route("/principal_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def principal_attributes(query: TableQueryDto):
    with g.database.Session.begin() as session:
        principal_attributes: list[AttributeDto] = (
            PrincipalRepository.get_all_unique_attribute_kvs(
                session=session, search_term=query.search_term
            )
        )

        return render_template(
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=principal_attributes,
        )

from app_logger import Logger, get_logger
from extensions import oidc
from flask import (
    Blueprint,
    Response,
    abort,
    g,
    make_response,
    redirect,
    render_template,
)
from flask import session as flask_session
from flask_pydantic import validate
from models import AttributeDto, PolicyAttributeDbo, PolicyDbo, WebSession
from repositories import DataObjectRepository, PolicyRepository, PrincipalRepository
from views.models import PolicyAttributeDto, PolicyMetadataDto, TableQueryDto
from opa import RegoGenerator

bp = Blueprint("policies", __name__, url_prefix="/policies")

logger: Logger = get_logger("views.policy")


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    response: Response = make_response(
        render_template("partials/policies/policies-search.html")
    )
    return response


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
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/create", methods=["POST"])
@oidc.oidc_auth("default")
@validate()
def create_policy():
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.create(
            session=session, logged_in_user=web_session.username
        )
        policy.status = PolicyDbo.STATUS_DRAFT
        session.add(policy)
        session.flush()
        policy_id = policy.policy_id
        session.commit()

    return redirect(f"/policies/{policy_id}", code=303)


@bp.route("/<policy_id>/clone", methods=["POST"])
@oidc.oidc_auth("default")
@validate()
def clone_policy(policy_id: int):
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.clone(
            session=session, policy_id=policy_id, logged_in_user=web_session.username
        )
        session.add(policy)
        session.commit()

    response: Response = make_response(
        render_template("partials/policies/policies-search.html")
    )
    response.headers.set(
        "HX-Trigger", '{"toast_success": {"message": "Cloned Successfully"}}'
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
            policy_id=policy_id,
            policy=policy,
        )


@bp.route("/<policy_id>/detail-modal", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_policy_modal(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policies/policy-detail-modal.html",
                policy=policy,
            )
        )
    return response


@bp.route("/<policy_id>/status/<status>", methods=["POST"])
@oidc.oidc_auth("default")
@validate()
def set_policy_status(policy_id: int, status: str):
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        if status == "request-publish":
            policy.status = PolicyDbo.STATUS_PENDING_PUBLISH
        elif status == "request-delete":
            policy.status = PolicyDbo.STATUS_PENDING_DELETE
        elif status == "published":
            policy.status = PolicyDbo.STATUS_PUBLISHED
            policy.publisher = web_session.username
        elif status == "draft":
            policy.status = PolicyDbo.STATUS_DRAFT
        elif status == "disabled":
            policy.status = PolicyDbo.STATUS_DISABLED
        else:
            abort(400, "Invalid status")

        policy.record_updated_by = web_session.username
        session.commit()

    response: Response = make_response(
        render_template("partials/policies/policies-search.html")
    )
    response.headers.set(
        "HX-Trigger-After-Swap",
        '{"toast_success": {"message": "Policy Updated Successfully"}}',
    )
    return response


@bp.route("/<policy_id>", methods=["DELETE"])
@oidc.oidc_auth("default")
@validate()
def delete_policy(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")
        session.delete(policy)
        session.commit()

    response: Response = make_response(
        render_template("partials/policies/policies-search.html")
    )
    response.headers.set(
        "HX-Trigger-After-Swap",
        '{"toast_success": {"message": "Deleted Successfully"}}',
    )
    return response


@bp.route("/<policy_id>/metadata_tab", methods=["GET"])
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
            policy_id=policy_id,
        )


@bp.route("/<policy_id>/metadata", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def update_policy_metadata(policy_id: int, body: PolicyMetadataDto):
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        policy.name = body.name
        policy.description = body.description
        policy.record_updated_by = web_session.username
        policy.author = web_session.username
        session.commit()

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
                active_tab="metadata",
                policy=body,
                policy_id=policy_id,
            )
        )

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


@bp.route("/<policy_id>/principal_attributes_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_principal_attributes_tab(policy_id: int):
    return render_template(
        template_name_or_list="partials/policy_builder/policy-builder-principal-attributes.html",
        active_tab="principals",
        policy_id=policy_id,
    )


@bp.route("/<policy_id>/principal_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_principal_attribute(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=policy.principal_attributes,
        )


@bp.route("/<policy_id>/principal_attributes", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def put_principal_attributes(policy_id: int, body: PolicyAttributeDto):
    # TODO regex the attributes to ensure they are legit
    # TODO auth the attributes

    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL,
            merge_attributes=body.attributes,
        )
        session.commit()

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-principal-attributes.html",
                active_tab="principals",
                policy_id=policy_id,
            )
        )

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


@bp.route("/<policy_id>/object_attributes_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_object_attributes_tab(policy_id: int):
    return render_template(
        template_name_or_list="partials/policy_builder/policy-builder-object-attributes.html",
        active_tab="objects",
        policy_id=policy_id,
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
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=policy.object_attributes,
        )


@bp.route("/<policy_id>/object_attributes", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def put_object_attributes(policy_id: int, body: PolicyAttributeDto):
    # TODO regex the attributes to ensure they are legit
    # TODO auth the attributes

    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_OBJECT,
            merge_attributes=body.attributes,
        )
        session.commit()

    response: Response = make_response(
        render_template(
            template_name_or_list="partials/policy_builder/policy-builder-object-attributes.html",
            active_tab="objects",
            policy_id=policy_id,
        )
    )

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


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


@bp.route("/<policy_id>/dsl_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_dsl_tab(policy_id: int):
    rego_generator: RegoGenerator = RegoGenerator(database=g.database)
    policy_dsl: str = rego_generator.generate_snippet_for_policy(policy_id)

    return render_template(
        template_name_or_list="partials/policy_builder/policy-builder-dsl.html",
        active_tab="dsl",
        policy_id=policy_id,
        policy_dsl=policy_dsl,
    )
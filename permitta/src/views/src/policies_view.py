import json
from datetime import datetime, timezone

from app_logger import Logger, get_logger
from auth import OpaPermittaAuthzActionEnum
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
from views.controllers import AuthzController
from views.models import (
    AttributeListVm,
    PolicyCreateVm,
    PolicyDslVm,
    PolicyMetadataVm,
    TableQueryVm,
)

from opa import RegoGenerator

bp = Blueprint("policies", __name__, url_prefix="/policies")

logger: Logger = get_logger("views.policy")

DEFAULT_SORT_KEY: str = "name"


@bp.route("/", methods=["GET"])
@oidc.oidc_auth("default")
def index():
    query_state: TableQueryVm = TableQueryVm(sort_key=DEFAULT_SORT_KEY)
    response: Response = make_response(
        render_template(
            "partials/policies/policies-search.html", query_state=query_state
        )
    )
    return response


@bp.route("/table", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def policies_table(query: TableQueryVm):
    with g.database.Session.begin() as session:
        policy_count, policies = PolicyRepository.get_all_with_search_and_pagination(
            session=session,
            sort_col_name=query.sort_key,  # TODO is this SQL injection?
            page_number=query.page_number,
            page_size=query.page_size,
            search_term=query.search_term,
        )

        query.record_count = policy_count
        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policies/policies-table.html",
                policies=policies,
                policy_count=policy_count,
                query_state=query,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/create", methods=["POST"])
@oidc.oidc_auth("default")
@validate()
def create_policy(body: PolicyCreateVm):
    web_session: WebSession = WebSession(flask_session=flask_session)

    with g.database.Session.begin() as session:
        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.CREATE_POLICY,
            object_state="New",
        )

        policy: PolicyDbo = PolicyRepository.create(
            session=session, logged_in_user=web_session.username
        )
        policy.status = PolicyDbo.STATUS_DRAFT
        policy.policy_type = body.policy_type.value
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
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.CLONE_POLICY,
            object_state=policy.status,
        )

        cloned_policy: PolicyDbo = PolicyRepository.clone(
            session=session, policy_id=policy_id, logged_in_user=web_session.username
        )

        session.add(cloned_policy)
        session.commit()

    response: Response = make_response(
        render_template(
            "partials/policies/policies-search.html",
            query_state=TableQueryVm(sort_key=DEFAULT_SORT_KEY),
        )
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

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder.html",
                active_tab="metadata",
                policy_id=policy_id,
                policy=policy,
                policy_type=policy.policy_type,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


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
            new_policy_status = PolicyDbo.STATUS_PENDING_PUBLISH
            action = OpaPermittaAuthzActionEnum.REQUEST_PUBLISH_POLICY
        elif status == "request-delete":
            new_policy_status = PolicyDbo.STATUS_PENDING_DELETE
            action = OpaPermittaAuthzActionEnum.REQUEST_DISABLE_POLICY
        elif status == "published":
            new_policy_status = PolicyDbo.STATUS_PUBLISHED
            policy.publisher = web_session.username
            action = OpaPermittaAuthzActionEnum.PUBLISH_POLICY
        elif status == "disabled":
            new_policy_status = PolicyDbo.STATUS_DISABLED
            action = OpaPermittaAuthzActionEnum.DISABLE_POLICY
        else:
            abort(400, "Invalid status")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=action,
            object_state=policy.status,
        )

        if not policy:
            abort(404, "Policy not found")

        policy.status = new_policy_status
        policy.record_updated_by = web_session.username
        session.commit()

    response: Response = make_response(
        render_template(
            "partials/policies/policies-search.html",
            query_state=TableQueryVm(sort_key=DEFAULT_SORT_KEY),
        )
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
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.DELETE_POLICY,
            object_state=policy.status,
        )

        session.delete(policy)
        session.commit()

    response: Response = make_response(
        render_template(
            "partials/policies/policies-search.html",
            query_state=TableQueryVm(sort_key=DEFAULT_SORT_KEY),
        )
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

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
                active_tab="metadata",
                policy=policy,
                policy_id=policy_id,
                policy_type=policy.policy_type,
            )
        )
    response.headers.set("HX-Trigger-After-Swap", "initialiseFlowbite")
    return response


@bp.route("/<policy_id>/metadata", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def update_policy_metadata(policy_id: int, body: PolicyMetadataVm):
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.EDIT_POLICY,
            object_state=policy.status,
        )

        policy.name = body.name
        policy.description = body.description
        policy.record_updated_by = web_session.username
        policy.author = web_session.username
        policy.record_updated_date = datetime.utcnow().replace(tzinfo=timezone.utc)

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-metadata.html",
                active_tab="metadata",
                policy=policy,
                policy_id=policy_id,
                policy_type=policy.policy_type,
            )
        )
        session.commit()

    response.headers.set(
        "HX-Trigger-After-Swap",
        '{"toast_success": {"message": "Saved Successfully"}, "initialiseFlowbite":{}}',
    )
    return response


@bp.route("/<policy_id>/principal_attributes_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_principal_attributes_tab(policy_id: int):
    query_state: TableQueryVm = TableQueryVm(sort_key="user_name")

    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder-principal-attributes.html",
            active_tab="principals",
            policy_id=policy_id,
            policy_type=policy.policy_type,
            query_state=query_state,
        )


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

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-attributes.html",
                attributes=policy.principal_attributes,
                attribute_list_name="policy-principal-attributes",
            )
        )

    response.headers.set("HX-Trigger-After-Swap", "policy-attribute-changed")
    return response


@bp.route("/<policy_id>/principal_attributes", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def put_principal_attributes(policy_id: int, body: AttributeListVm):
    # TODO regex the attributes to ensure they are legit
    # TODO auth the attributes
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.EDIT_POLICY,
            object_state=policy.status,
        )

        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL,
            merge_attributes=body.attribute_list,
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-attributes.html",
                attributes=policy.principal_attributes,
                attribute_list_name="policy-principal-attributes",
            )
        )
        session.commit()

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


@bp.route("/<policy_id>/object_attributes_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_object_attributes_tab(policy_id: int):
    query_state: TableQueryVm = TableQueryVm(
        sort_key="tables.table_name", scope="tables"
    )

    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        return render_template(
            template_name_or_list="partials/policy_builder/policy-builder-object-attributes.html",
            active_tab="objects",
            policy_id=policy_id,
            policy_type=policy.policy_type,
            query_state=query_state,
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

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-attributes.html",
                attributes=policy.object_attributes,
                attribute_list_name="policy-object-attributes",
            )
        )

    response.headers.set("HX-Trigger-After-Swap", "policy-attribute-changed")
    return response


@bp.route("/<policy_id>/object_attributes", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def put_object_attributes(policy_id: int, body: AttributeListVm):
    # TODO regex the attributes to ensure they are legit
    # TODO auth the attributes

    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.EDIT_POLICY,
            object_state=policy.status,
        )

        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_OBJECT,
            merge_attributes=body.attribute_list,
        )

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-attributes.html",
                attributes=policy.object_attributes,
                attribute_list_name="policy-principal-attributes",
            )
        )
        session.commit()

    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response


@bp.route("/create/all_principal_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def all_principal_attributes(query: TableQueryVm):
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
            attribute_list_name="all-principal-attributes",
        )


@bp.route("/create/all_object_attributes", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def all_object_attributes(query: TableQueryVm):
    with g.database.Session.begin() as session:
        object_attributes: list[AttributeListVm] = (
            DataObjectRepository.get_all_unique_attributes(
                session=session, search_term=query.search_term
            )
        )

        return render_template(
            template_name_or_list="partials/policy_builder/policy-attributes.html",
            attributes=object_attributes,
            attribute_id_prefix="object_attribute",
            attribute_list_name="all-object-attributes",
        )


@bp.route("/<policy_id>/dsl_tab", methods=["GET"])
@oidc.oidc_auth("default")
@validate()
def get_dsl_tab(policy_id: int):
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        policy_dsl: str = RegoGenerator.generate_snippet_for_policy(policy=policy)
        policy_dsl_read_only: bool = policy.policy_type == PolicyDbo.POLICY_TYPE_BUILDER

        response: Response = make_response(
            render_template(
                template_name_or_list="partials/policy_builder/policy-builder-dsl.html",
                active_tab="dsl",
                policy_id=policy_id,
                policy_dsl=policy_dsl,
                policy_type=policy.policy_type,
                policy_dsl_read_only=policy_dsl_read_only,
            )
        )

        trigger_content: dict = {
            "load_codemirror": {"readonly": str(policy_dsl_read_only)}
        }

    response.headers.set(
        "HX-Trigger-After-Settle",
        json.dumps(trigger_content),
    )
    return response


@bp.route("/<policy_id>/dsl", methods=["PUT"])
@oidc.oidc_auth("default")
@validate()
def put_dsl(policy_id: int, body: PolicyDslVm):
    web_session: WebSession = WebSession(flask_session=flask_session)
    with g.database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )

        if not policy:
            abort(404, "Policy not found")

        AuthzController().authorize(
            session=session,
            user_name=web_session.username,
            action=OpaPermittaAuthzActionEnum.EDIT_POLICY,
            object_state=policy.status,
        )

        # TODO validate DSL
        if policy.policy_type != PolicyDbo.POLICY_TYPE_DSL:
            abort(400, "Incorrect policy type")

        policy.policy_dsl = body.policy_dsl
        session.commit()

    response: Response = make_response("", 200)
    response.headers.set(
        "HX-Trigger-After-Swap", '{"toast_success": {"message": "Saved Successfully"}}'
    )
    return response

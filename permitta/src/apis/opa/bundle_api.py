import gzip
from itertools import chain
from app_logger import Logger, get_logger
logger: Logger = get_logger("opa.bundle_api")

from repositories import PrincipalRepository
from models import PrincipalDbo, PrincipalAttributeDbo
from flask import (
    Blueprint,
    request,
g, jsonify
)

bp = Blueprint("opa_bundle", __name__, url_prefix="/opa/bundle")


@bp.route("", methods=["GET"])
def bundle():
    with g.database.Session.begin() as session:
        principal_count, principals = PrincipalRepository.get_all(session=session)
        logger.info(f"Retrieved {principal_count} principals")

        principals_json: list[dict] = []
        for principal in principals:
            pj: dict = {
                "user": principal.user_name,
                "attributes": [
                    {
                        "key": p.attribute_key,
                        "value": p.attribute_value
                    }
                    for p in chain(principal.principal_attributes, principal.group_membership_attributes)
                ]
            }
            principals_json.append(pj)

        # add data objects + rego

    return jsonify(principals_json)

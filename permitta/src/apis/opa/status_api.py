import gzip
import json

from app_logger import Logger, get_logger
from flask import Blueprint, g, request
from flask_pydantic import validate

from .status_dto import StatusDto

bp = Blueprint("opa_status", __name__, url_prefix="/opa/status")
logger: Logger = get_logger("opa.status_api")


@bp.route("", methods=["POST"])
@validate()
def post(body: StatusDto) -> str:
    logger.info(
        f"Received status update from OPA: {body.bundles.trino.name} {body.labels.id}"
    )
    logger.info(body.json())

    return "ok"

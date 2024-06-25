from flask import Blueprint, jsonify
from app_logger import Logger, get_logger

logger: Logger = get_logger("views.healthz")
bp = Blueprint("healthz", __name__, url_prefix="/healthz")


@bp.route("/", methods=["GET"])
def get():
    logger.info("healthz: GET")
    return jsonify({"status": "ok"})

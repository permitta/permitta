from flask import Blueprint, jsonify

bp = Blueprint("healthz", __name__, url_prefix="/healthz")


@bp.route("/", methods=["GET"])
def get():
    return jsonify({"status": "ok"})

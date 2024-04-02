from flask import Blueprint, jsonify, session as flask_session

bp = Blueprint('healthz', __name__, url_prefix='/healthz')


@bp.route('/', methods=['GET'])
def get():
    return jsonify(flask_session)

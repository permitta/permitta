from app_config import AppConfigModelBase
from database import Database
from extensions import oidc, oidc_auth_provider
from flask import Blueprint, Flask, g, render_template


class FlaskConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "flask"
    secret_key: str = None
    static_url_path: str = ""
    static_folder: str = "../ui/static"
    template_folder: str = "../ui/templates"


# bp = Blueprint("a", __name__, url_prefix="/temp")


def create_app() -> Flask:
    # global oidc

    flask_config = FlaskConfig.load()

    flask_app = Flask(
        __name__,
        static_url_path=flask_config.static_url_path,
        static_folder=flask_config.static_folder,
        template_folder=flask_config.template_folder,
    )
    flask_app.secret_key = flask_config.secret_key

    # OIDC

    flask_app.config.update(
        OIDC_REDIRECT_URI=oidc_auth_provider.oidc_auth_provider_config.redirect_uri
    )
    oidc.init_app(flask_app)

    # blueprints
    from views import (
        data_objects_bp,
        groups_bp,
        healthz_bp,
        policies_bp,
        principals_bp,
        root_bp,
    )

    flask_app.register_blueprint(root_bp)
    flask_app.register_blueprint(principals_bp)
    flask_app.register_blueprint(healthz_bp)
    flask_app.register_blueprint(data_objects_bp)
    flask_app.register_blueprint(policies_bp)
    flask_app.register_blueprint(groups_bp)

    # Database
    database: Database = Database()
    database.connect()

    @flask_app.before_request
    def before_request():
        # connect DB
        g.database = database

    @flask_app.route("/logout")
    @oidc.oidc_logout
    def logout():
        return "logged out"

    return flask_app


# @bp.route("/")
# @oidc.oidc_auth("default")
# def dashboard():
#     return render_template("views/dashboard.html")

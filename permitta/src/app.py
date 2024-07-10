from datetime import datetime, timezone

from apis import opa_bundle_api_bp, opa_decision_logs_api_bp, opa_status_api_bp
from app_config import AppConfigModelBase
from app_logger import Logger, get_logger
from auth import OpaAuthzProvider
from database import Database
from extensions import oidc, oidc_auth_provider
from flask import Flask, g, redirect, request

# blueprints
from views import (
    data_objects_bp,
    decision_logs_bp,
    groups_bp,
    healthz_bp,
    policies_bp,
    principals_bp,
    root_bp,
)

logger: Logger = get_logger("app")


class FlaskConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "flask"
    secret_key: str = None
    static_url_path: str = ""
    static_folder: str = "../ui/static"
    template_folder: str = "../ui/templates"


def create_app(database: Database | None = None) -> Flask:
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

    flask_app.register_blueprint(root_bp)
    flask_app.register_blueprint(principals_bp)
    flask_app.register_blueprint(healthz_bp)
    flask_app.register_blueprint(data_objects_bp)
    flask_app.register_blueprint(policies_bp)
    flask_app.register_blueprint(groups_bp)
    flask_app.register_blueprint(decision_logs_bp)

    flask_app.register_blueprint(opa_bundle_api_bp)
    flask_app.register_blueprint(opa_decision_logs_api_bp)
    flask_app.register_blueprint(opa_status_api_bp)

    # Database
    database: Database = Database()
    database.connect()

    # AuthZ - set the policy doc on OPA at startup
    authz: OpaAuthzProvider = OpaAuthzProvider(user_name="app", user_attributes=[])
    authz.apply_policy_to_opa()

    @flask_app.before_request
    def before_request():
        # connect DB
        g.database = database

    @flask_app.after_request
    def after_request(response):
        timestamp = datetime.now(tz=timezone.utc).strftime("[%Y-%b-%d %H:%M]")
        logger.info(
            "%s %s %s %s %s %s",
            timestamp,
            request.remote_addr,
            request.method,
            request.scheme,
            request.full_path,
            response.status,
        )
        return response

    @flask_app.route("/logout")
    @oidc.oidc_logout
    def logout():
        return redirect("/")

    return flask_app

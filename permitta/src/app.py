from app_config import AppConfigModelBase
from auth import OidcAuthProvider
from database import Database
from flask import Flask, g, render_template


class FlaskConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "flask"
    secret_key: str = None
    static_url_path: str = ""
    static_folder: str = "../ui/static"
    template_folder: str = "../ui/templates"


flask_config = FlaskConfig.load()

flask_app = Flask(
    __name__,
    static_url_path=flask_config.static_url_path,
    static_folder=flask_config.static_folder,
    template_folder=flask_config.template_folder,
)
flask_app.secret_key = flask_config.secret_key

# blueprints
from views import healthz_bp, principals_bp

flask_app.register_blueprint(principals_bp)
flask_app.register_blueprint(healthz_bp)

# TODO add this to the oidc thing
flask_app.config.update(OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback")
oidc_auth_provider: OidcAuthProvider = OidcAuthProvider()
oidc_auth_provider.init_app(flask_app=flask_app)

# Database
database: Database = Database()
database.connect()


@flask_app.before_request
def before_request():
    # OIDC token check
    # connect DB
    g.database = database


@flask_app.teardown_request
def teardown_request(request):
    try:
        pass
    except Exception as e:
        # TODO log me
        pass


@flask_app.route("/")
def dashboard():
    return render_template("views/dashboard.html")


@flask_app.route("/policies")
def policies():
    return render_template("views/policies.html")


@flask_app.route("/principals")
def principals():
    return render_template("views/principals.html")


@flask_app.route("/attributes")
@flask_app.route("/")
def attributes():
    return render_template("views/attributes.html")


@flask_app.route("/logout")
@oidc_auth_provider.auth.oidc_logout
def logout():
    return "logged out"

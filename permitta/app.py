from flask import Flask, session, jsonify, render_template
from flask_pyoidc.user_session import UserSession

from views import ApiRegistrar
from auth import OidcAuthProvider


flask_app = Flask(__name__)
flask_app.secret_key = "jhfreakjwsdnfkjlsnd"  # SECRET_KEY


# TODO add to oidc thing
flask_app.config.update(OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback")
oidc_auth_provider: OidcAuthProvider = OidcAuthProvider()
oidc_auth_provider.init_app(flask_app=flask_app)

api_registrar: ApiRegistrar = ApiRegistrar()
api_registrar.init_app(flask_app=flask_app)

class PermittaSession(UserSession):
    @property
    def given_name(self) -> str:
        return self.userinfo.get("given_name")

    @property
    def family_name(self) -> str:
        return self.userinfo.get("family_name")

    @property
    def email(self) -> str:
        return self.userinfo.get("email")


@flask_app.route("/")
@oidc_auth_provider.auth.oidc_auth(OidcAuthProvider.PROVIDER_NAME)
def index():
    permitta_session = PermittaSession(session)
    # return f"Hello {permitta_session.given_name} {permitta_session.family_name} with email {permitta_session.email}"
    return render_template("index.html")


@flask_app.route("/hello")
@oidc_auth_provider.auth.oidc_auth(OidcAuthProvider.PROVIDER_NAME)


def hello():
    # user_session = UserSession(session)
    return "hello"


@flask_app.route("/logout")
# @auth.oidc_logout
def logout():
    return "logged out"


# @auth.error_view
# def error(error=None, error_description=None):
#     return jsonify({"error": error, "message": error_description})

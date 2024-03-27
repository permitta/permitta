from flask import Flask, session, jsonify, render_template
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.user_session import UserSession

PROVIDER_NAME: str = "keycloak"
provider_config: ProviderConfiguration = ProviderConfiguration(
    issuer="http://localhost:8080/realms/permitta",
    client_metadata=ClientMetadata(
        client_id="permitta-client", client_secret="AuSlZ8hJoEPcwX6jjTsIx6JXHIYbZLkE"
    ),
)

app = Flask(__name__)
app.config.update(OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback")
app.secret_key = "jhfreakjwsdnfkjlsnd"  # SECRET_KEY

auth = OIDCAuthentication({PROVIDER_NAME: provider_config})
auth.init_app(app)


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


@app.route("/")
@auth.oidc_auth(PROVIDER_NAME)
def index():
    permitta_session = PermittaSession(session)
    # return f"Hello {permitta_session.given_name} {permitta_session.family_name} with email {permitta_session.email}"
    return render_template("index.html")


@app.route("/hello")
@auth.oidc_auth(PROVIDER_NAME)
def hello():
    user_session = UserSession(session)
    return "hello"


@app.route("/logout")
@auth.oidc_logout
def logout():
    return "logged out"


@app.route("/healthz")
def healthz():
    return "healthy"


@auth.error_view
def error(error=None, error_description=None):
    return jsonify({"error": error, "message": error_description})

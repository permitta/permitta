import json
import logging

from flask import Flask, session, jsonify
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.user_session import UserSession

PROVIDER_NAME: str = "keycloak"
provider_config: ProviderConfiguration = ProviderConfiguration(
    issuer="http://localhost:8080/realms/permitta",
    client_metadata=ClientMetadata(client_id="permitta-client", client_secret="AuSlZ8hJoEPcwX6jjTsIx6JXHIYbZLkE"),
)

app = Flask(__name__)
app.config.update(OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback")
app.secret_key = "jhfreakjwsdnfkjlsnd"  # SECRET_KEY

auth = OIDCAuthentication({PROVIDER_NAME: provider_config})
auth.init_app(app)


@app.route("/")
@auth.oidc_auth(PROVIDER_NAME)
def index():
    user_session = UserSession(session)
    return "ok"

@app.route("/hello")
@auth.oidc_auth(PROVIDER_NAME)
def hello():
    user_session = UserSession(session)
    return "hello"

@app.route("/logout")
@auth.oidc_logout
def logout():
    # user_session = UserSession(session)
    return "logged out  "

@app.route("/healthz")
def healthz():
    # user_session = UserSession(session)
    return "logged out  "

@auth.error_view
def error(error=None, error_description=None):
    return jsonify({"error": error, "message": error_description})

from flask.views import MethodView
from flask import session as flask_session
from auth import OidcAuthProvider
from models import WebSession


class ViewBase(MethodView):
    ROUTE_PREFIX: str = ""

    session: WebSession = None
    oidc_auth_provider: OidcAuthProvider | None = None

    def __init__(self, model, oidc_auth_provider: OidcAuthProvider):
        self.oidc_auth_provider = oidc_auth_provider
        self.session = WebSession(flask_session=flask_session)

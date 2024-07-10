import os

from auth import OidcAuthProvider
from flask_pyoidc import OIDCAuthentication

# HACK, can we do better than this?
test_mode: bool = bool(os.getenv("FLASK_TESTING", "False").lower() == "true")

oidc_auth_provider: OidcAuthProvider = OidcAuthProvider(test_mode=test_mode)
oidc: OIDCAuthentication = oidc_auth_provider.oidc_auth

from auth import OidcAuthProvider
from flask_pyoidc import OIDCAuthentication

oidc_auth_provider: OidcAuthProvider = OidcAuthProvider()
oidc: OIDCAuthentication = oidc_auth_provider.oidc_auth

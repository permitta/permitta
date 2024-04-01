from flask import Flask
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ClientMetadata, ProviderConfiguration
from .oidc_auth_provider_config import OidcAuthProviderConfig


class OidcAuthProvider:
    PROVIDER_NAME: str = "default"
    auth: OIDCAuthentication

    def init_app(self, flask_app: Flask):
        oidc_auth_provider_config: OidcAuthProviderConfig = (
            OidcAuthProviderConfig.load()
        )

        provider_config: ProviderConfiguration = ProviderConfiguration(
            issuer=oidc_auth_provider_config.issuer,
            client_metadata=ClientMetadata(
                client_id=oidc_auth_provider_config.client_id,
                client_secret=oidc_auth_provider_config.client_secret,
            ),
        )
        self.auth = OIDCAuthentication({self.PROVIDER_NAME: provider_config})
        self.auth.init_app(flask_app)

    def require_oidc_auth(self):
        return self.auth.oidc_auth

    def oidc_logout(self):
        return self.auth.oidc_logout

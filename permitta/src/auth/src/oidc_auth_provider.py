from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ClientMetadata, ProviderConfiguration

from .oidc_auth_provider_config import OidcAuthProviderConfig


class OidcAuthProvider:
    PROVIDER_NAME: str = "default"

    @property
    def oidc_auth(self) -> OIDCAuthentication:
        if not self._oidc_auth:
            self._oidc_auth = self._get_oidc_auth()
        return self._oidc_auth

    def __init__(self):
        self._oidc_auth: OIDCAuthentication | None = None
        self.oidc_auth_provider_config: OidcAuthProviderConfig = (
            OidcAuthProviderConfig.load()
        )

    def _get_oidc_auth(self) -> OIDCAuthentication:
        provider_config: ProviderConfiguration = ProviderConfiguration(
            issuer=self.oidc_auth_provider_config.issuer,
            client_metadata=ClientMetadata(
                client_id=self.oidc_auth_provider_config.client_id,
                client_secret=self.oidc_auth_provider_config.client_secret,
            ),
        )
        return OIDCAuthentication({self.PROVIDER_NAME: provider_config})

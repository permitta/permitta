import functools

from app_logger import Logger, get_logger
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ClientMetadata, ProviderConfiguration

from .oidc_auth_provider_config import OidcAuthProviderConfig

logger: Logger = get_logger("auth.oidc_auth_provider")


class OidcAuthProvider:
    PROVIDER_NAME: str = "default"

    @property
    def oidc_auth(self) -> OIDCAuthentication:
        if not self._oidc_auth:
            self._oidc_auth = self._get_oidc_auth()
        return self._oidc_auth

    def __init__(self, test_mode: bool = False) -> None:
        self._oidc_auth: OIDCAuthentication | None = None
        self.oidc_auth_provider_config: OidcAuthProviderConfig = (
            OidcAuthProviderConfig.load()
        )
        self._test_mode = test_mode

    def _get_oidc_auth(self):
        if self._test_mode:
            return self._get_oidc_auth_mock()
        else:
            return self._get_oidc_auth_service()

    def _get_oidc_auth_service(self) -> OIDCAuthentication:
        provider_config: ProviderConfiguration = ProviderConfiguration(
            issuer=self.oidc_auth_provider_config.issuer,
            client_metadata=ClientMetadata(
                client_id=self.oidc_auth_provider_config.client_id,
                client_secret=self.oidc_auth_provider_config.client_secret,
            ),
        )
        return OIDCAuthentication({self.PROVIDER_NAME: provider_config})

    def _get_oidc_auth_mock(self):
        class OidcMock:
            def init_app(self, flask_app) -> None:
                pass

            def oidc_logout(self, param):
                def oidc_decorator(view_func):
                    @functools.wraps(view_func)
                    def wrapper(*args, **kwargs):
                        logger.warning(
                            "Using mock OIDC authenticator - user is not authenticated"
                        )

                    return wrapper

                return oidc_decorator

            def oidc_auth(self, provider_name: str):
                def oidc_decorator(view_func):
                    @functools.wraps(view_func)
                    def wrapper(*args, **kwargs):
                        logger.warning(
                            "Using mock OIDC authenticator - user is not authenticated"
                        )
                        return view_func(*args, **kwargs)

                    return wrapper

                return oidc_decorator

        return OidcMock()

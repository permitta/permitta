from app_config import AppConfigModelBase


class OidcAuthProviderConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "oidc_auth_provider"
    issuer: str = None
    client_id: str = None
    client_secret: str = None
    redirect_uri: str = "http://127.0.0.1:8000/oidccallback"

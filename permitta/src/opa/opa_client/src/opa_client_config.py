from app_config import AppConfigModelBase


class OpaClientConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "opa_client"

    scheme: str = "http"
    hostname: str = "localhost"
    port: int = 8181
    path: str = "/v1/data/permitta/authz"

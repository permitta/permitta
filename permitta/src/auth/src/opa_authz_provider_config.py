from urllib.parse import urljoin

from app_config import AppConfigModelBase


class OpaAuthzProviderConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "opa_authz_provider"

    @property
    def url(self) -> str:
        return urljoin(f"{self.scheme}://{self.host}:{self.port}", self.path)

    scheme: str = None
    host: str = None
    port: str = None
    path: str = None
    policy_name: str = None
    policy_file_path: str = None

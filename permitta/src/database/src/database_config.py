from app_config import AppConfigModelBase


class DatabaseConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "database"
    connection_string: str = None

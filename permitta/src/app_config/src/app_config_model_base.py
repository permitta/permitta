import os
import re
import yaml

class AppConfigModelBase:
    """
    Configuration parameter syntax:
    <module>.<submodule>.<property_name>: <value>
    ingestor.json_file.file_path: ./data.json

    Each module will request its own configuration values and bind them
    to a model class they own

    This class is passed the model dataclass, and <module>.<submodule>
    and the hydrated dataclass is returned
    """

    CONFIG_PREFIX: str = "base"

    @classmethod
    def load(cls) -> "AppConfigModelBase":
        config_file_path: str = os.getenv("CONFIG_FILE_PATH", "config.yaml")
        with open(config_file_path, "r") as f:
            config_content: dict = yaml.load(f, Loader=yaml.FullLoader)

        instance = cls()
        for key, value in config_content.items():
            attr_name: str = key.removeprefix(f"{cls.CONFIG_PREFIX}.")

            # support merging in $ENV_VAR syntax
            for match in re.findall(r"(\$[A-Z_]*)", value):
                value = value.replace(match, os.getenv(match[1:], ""))

            if hasattr(instance, attr_name):
                setattr(instance, attr_name, value)
        return instance

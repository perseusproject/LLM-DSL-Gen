import logging
import os
from pathlib import Path
from .utils import SafeNamespace
import tomli

logger = logging.getLogger("dsl_gen")


class ConfigLoader:
    """
    A singleton class responsible for loading and parsing configuration files.
    Methods
    """
    # Skip if you do not know what a singleton is, this is not important for
    # the project neither.
    _instance = None

    def __new__(cls, env_var):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(env_var)
        return cls._instance

    def _load_config(self, env_var: str):
        """Convert TOML configuration to nested objects"""
        config_path = os.getenv(env_var)
        if not config_path:
            raise EnvironmentError(
                f"Environment variable {env_var} must be set"
            )

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file does not exist: {config_file}"
            )

        with open(config_file, "rb") as f:
            raw_config = tomli.load(f)

        self.config = self._dict_to_namespace(raw_config)

    def _dict_to_namespace(self, data: dict) -> SafeNamespace:
        """Recursively convert dictionary to object attributes"""
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._dict_to_namespace(value)
        return SafeNamespace(**data)


class APILoader(ConfigLoader):
    # Subclass that maintains its own singleton reference
    # Again, skip if you are unfamiliar with the singleton pattern
    _instance = None

    def __new__(cls, env_var):
        if cls._instance is None:
            cls._instance = super().__new__(cls, env_var)
            cls._instance._load_config(env_var)
        return cls._instance


try:
    # What you need to know:
    # The following code initializes the CFG and API objects
    # by reading your os environment variables
    CFG = ConfigLoader("LLM_DSL_CONFIG_PATH").config
    API = APILoader("LLM_DSL_API_PATH").config

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Configuration initialized: %s", CFG)
    else:
        logger.info("Configuration initialized")

except Exception as e:
    raise RuntimeError(f"Configuration initialization failed: {e}") from e

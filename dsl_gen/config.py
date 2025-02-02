import os
from pathlib import Path
import tomli
import logging

from types import SimpleNamespace

class ConfigLoader:
    _instance = None

    def __new__(cls, env_var: str = "LLM_DSL_CONFIG_PATH"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(env_var)
        return cls._instance

    def _load_config(self, env_var: str):
        """Convert TOML configuration to nested objects"""
        config_path = os.getenv(env_var)
        if not config_path:
            raise EnvironmentError(f"Environment variable {env_var} must be set")

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file does not exist: {config_file}")

        with open(config_file, "rb") as f:
            raw_config = tomli.load(f)

        # Convert dictionary to nested objects
        self.config = self._dict_to_namespace(raw_config)

    def _dict_to_namespace(self, data: dict) -> SimpleNamespace:
        """Recursively convert dictionary to object attributes"""
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._dict_to_namespace(value)
        return SimpleNamespace(**data)

# Singleton initialization
logger = logging.getLogger('global')

try:
    loader = ConfigLoader()
    CFG = loader.config
    logger.debug("Configuration initialized", CFG)
except Exception as e:
    raise RuntimeError(f"Configuration initialization failed: {e}") from e
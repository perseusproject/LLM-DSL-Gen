import logging
import os
from pathlib import Path
from types import SimpleNamespace
import tomli

logger = logging.getLogger("dsl_gen")


class SafeNamespace(SimpleNamespace):
    """Namespace that masks sensitive information when printed, with multiline indentation."""
    # Skip if you are unfamiliar with the __repr__ and __str__ methods, this is not important for the project
    # In a nutshell, we prevent the API key from being printed in the logs

    def __repr__(self) -> str:
        return self._safe_repr()

    def __str__(self) -> str:
        # Make str() output consistent with repr()
        return self._safe_repr()

    def _safe_repr(self, indent_level: int = 0) -> str:
        """
        Construct a multiline string similar to SimpleNamespace's repr,
        but mask 'api_key' fields and remove extra spaces around "=namespace(".
        """
        indent_str = "    " * indent_level
        child_indent_str = "    " * (indent_level + 1)

        lines = []
        lines.append(f"{indent_str}namespace(")

        items = []
        for k, v in self.__dict__.items():
            if isinstance(v, SafeNamespace):
                sub_repr = v._safe_repr(indent_level + 1)
                sub_lines = sub_repr.split("\n")

                if sub_lines:
                    sub_lines[0] = sub_lines[0].lstrip()

                final_sub_repr = "\n".join(sub_lines)
                items.append(f"{child_indent_str}{k}={final_sub_repr}")
            else:
                if k.lower() == "api_key":
                    items.append(f"{child_indent_str}{k}='****'")
                else:
                    items.append(f"{child_indent_str}{k}={repr(v)}")
        if items:
            lines.extend(items)
        lines.append(f"{indent_str})")
        return "\n".join(lines)


class ConfigLoader:
    """
    A singleton class responsible for loading and parsing configuration files.
    Methods
    """
    # Skip if you do not know what a singleton is, this is not important for the project neither.
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

    logger.info("Configuration initialized: %s", CFG)

except Exception as e:
    raise RuntimeError(f"Configuration initialization failed: {e}") from e

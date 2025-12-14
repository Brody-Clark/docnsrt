"""Configuration settings for docnsrt."""

import os
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field
import yaml
import re
from dataclasses_json import dataclass_json
from docnsrt.core.styles import DocstringStyle

@dataclass_json
@dataclass
class DocnsrtConfig:
    """Main configuration for the application."""

    project_dir: str = None
    files: List[str] = field(default_factory=lambda: ["*"])
    functions: List[str] = field(default_factory=lambda: ["*"])
    language: str = None
    style: str = DocstringStyle.BASIC.value
    ignore_files: List[str] = field(default_factory=list)
    ignore_functions: List[str] = field(default_factory=list)
    no_summary: bool = False
    check: bool = False
    write: bool = True
    force_all: bool = False
    log_level: str = "INFO"

    def get_default_style_enum(self) -> DocstringStyle:
        """Returns the default docstring style enum."""
        try:
            for style_enum_member in DocstringStyle:
                if style_enum_member.value.lower() == self.default_style.lower():
                    return style_enum_member
            raise ValueError(f"Invalid default_style '{self.default_style}' in config.")
        except AttributeError as exc:
            raise TypeError(
                f"default_style '{self.default_style}' is not a string type."
            ) from exc


class EnvVarLoader(yaml.SafeLoader):
    """
    A custom YAML loader that processes !ENV tags to pull values from environment variables.
    Supports a default fallback value using '|' (e.g., !ENV VAR_NAME | default_value).
    """


def construct_env_var(loader, node):
    """
    Constructor for the !ENV tag.
    It attempts to retrieve the environment variable.
    If a default value is provided (e.g., '!ENV VAR_NAME | default'), it uses that if the env var is not set.
    Otherwise, it raises a ValueError if the env var is missing and no default is provided.
    """
    value = loader.construct_scalar(node)

    # Split the value by '|' to separate variable name and optional default
    parts = [p.strip() for p in value.split("|", 1)]
    env_var_name = parts[0]
    default_value = parts[1] if len(parts) > 1 else None

    # Retrieve environment variable
    env_val = os.getenv(env_var_name)

    if env_val is None:
        if default_value is not None:
            # If default is provided, use it
            return default_value
        # If no default and env var is missing, raise an error
        raise ValueError(
            f"Environment variable '{env_var_name}' is not set "
            f"and no default value was provided for '!ENV {value}' in config."
        )
    return env_val


VAR_PATTERN = re.compile(r"\${\s*vars\.([A-Za-z0-9_]+)\s*}")


def load_project_config_yaml(
    path: str,
) -> dict:
    """
    Load YAML using EnvVarLoader (!ENV support) and resolve ${...} placeholders.
    Returns a resolved dict (doesn't construct dataclasses).
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.load(f, Loader=EnvVarLoader) or {}
    vars_dict = raw.get("vars", {})
    config = _resolve_vars(raw, vars_dict)
    return config


def _resolve_vars(config, vars_dict):
    if isinstance(config, dict):
        return {k: _resolve_vars(v, vars_dict) for k, v in config.items()}
    elif isinstance(config, list):
        return [_resolve_vars(v, vars_dict) for v in config]
    elif isinstance(config, str):
        return VAR_PATTERN.sub(lambda m: vars_dict.get(m.group(1), ""), config)
    return config


EnvVarLoader.add_constructor("!ENV", construct_env_var)

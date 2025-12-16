"""Configuration settings for docnsrt."""

import re
from typing import List
from dataclasses import dataclass, field
import yaml
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


VAR_PATTERN = re.compile(r"\${\s*vars\.([A-Za-z0-9_]+)\s*}")


def load_project_config_yaml(
    path: str,
) -> dict:
    """
    Load YAML configuration file with variable resolution.
    Returns a resolved dict (doesn't construct dataclasses).
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.load(f, Loader=yaml.FullLoader) or {}
    return raw

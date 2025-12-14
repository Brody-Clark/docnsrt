from unittest.mock import patch, mock_open
import pytest

from docnsrt.config import (
    _resolve_vars,
)

def test__resolve_vars_handles_nested_and_list_structures():
    config = {
        "vars": {"A": "1", "B": "two"},
        "top": "${vars.A}",
        "nested": {"x": "${vars.B}", "y": ["prefix ${vars.A}", {"z": "${vars.B}"}]},
    }
    vars_dict = config["vars"]
    resolved = _resolve_vars(config, vars_dict)

    assert resolved["top"] == "1"
    assert resolved["nested"]["x"] == "two"
    assert resolved["nested"]["y"][0] == "prefix 1"
    assert resolved["nested"]["y"][1]["z"] == "two"

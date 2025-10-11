from unittest.mock import patch, mock_open
import pytest

from docmancer.config import (
    load_project_config_yaml,
    _resolve_vars,
    EnvVarLoader,
)


def test_load_project_config_yaml_resolves_vars_and_uses_env_loader():
    # prepare the dict that yaml.load should return
    raw = {
        "vars": {"API_KEY": "sk_test_value"},
        "remote_api": {
            "headers": {"Authorization": "Bearer ${vars.API_KEY}", "X": "keep"},
            "payload_template": {"model": "llm-v1"},
        },
    }

    m_open = mock_open(read_data="dummy")
    # patch builtins.open and the yaml.load used inside docmancer.config
    with (
        patch("builtins.open", m_open),
        patch("docmancer.config.yaml.load", return_value=raw) as mock_yaml_load,
    ):
        result = load_project_config_yaml("some/path/.docmancer.yaml")

    # ensure yaml.load was called with the EnvVarLoader
    assert mock_yaml_load.call_count == 1
    _, kwargs = mock_yaml_load.call_args
    assert kwargs.get("Loader") is EnvVarLoader

    # assert placeholders were resolved using the vars section
    assert result["remote_api"]["headers"]["Authorization"] == "Bearer sk_test_value"
    assert result["remote_api"]["headers"]["X"] == "keep"


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

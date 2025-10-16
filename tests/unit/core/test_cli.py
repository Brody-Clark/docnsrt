import json
import sys
from pathlib import Path
import pytest
import docmancer.core.cli as cli


def test_parse_kv_pairs_basic():
    inp = ["Authorization=Bearer sk", "X-Flag:1", "BareKey"]
    out = cli._parse_kv_pairs(inp)
    assert out["Authorization"] == "Bearer sk"
    assert out["X-Flag"] == "1"
    assert out["BareKey"] == ""


def test_parse_json_or_file_inline_and_file(tmp_path):
    # inline JSON
    s = '{"a": 1, "b": [1,2]}'
    parsed = cli._parse_json_or_file(s)
    assert isinstance(parsed, dict)
    assert parsed["a"] == 1

    # file YAML
    p = tmp_path / "payload.yaml"
    p.write_text("model: llm-v1\nmessages:\n  - role: user\n")
    parsed2 = cli._parse_json_or_file(str(p))
    assert isinstance(parsed2, dict)
    assert parsed2["model"] == "llm-v1"


def test_find_and_load_config_handles_parsing_error(monkeypatch, tmp_path):
    # Create a fake config file path but make load_config raise to simulate parse error
    cfg_path = tmp_path / ".docmancer.yaml"
    cfg_path.write_text("invalid: : yaml")

    def _bad_load(p):
        raise ValueError("bad yaml")

    monkeypatch.setattr("docmancer.core.cli.load_config", _bad_load)
    # start search from tmp_path and expect (None, {}) return on parse failure
    path, cfg = cli.find_and_load_config(start_path=Path(tmp_path))
    assert path is None
    assert cfg == {}
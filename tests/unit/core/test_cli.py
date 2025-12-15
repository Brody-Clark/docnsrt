from pathlib import Path
import pytest
import docnsrt.core.cli as cli


def test_find_and_load_config_handles_parsing_error(monkeypatch, tmp_path):
    # Create a fake config file path but make load_config raise to simulate parse error
    cfg_path = tmp_path / ".docnsrt.yaml"
    cfg_path.write_text("invalid: : yaml")

    def _bad_load(p):
        raise ValueError("bad yaml")

    monkeypatch.setattr("docnsrt.core.cli.load_config", _bad_load)
    # start search from tmp_path and expect (None, {}) return on parse failure
    path, cfg = cli.find_and_load_config(start_path=Path(tmp_path))
    assert path is None
    assert cfg == {}

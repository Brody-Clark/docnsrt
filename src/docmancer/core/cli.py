"""CLI for Docmancer - a documentation generation tool."""

from pathlib import Path
import argparse
import os
import yaml
import json
from typing import Optional, List, Dict, Any
from docmancer.config import DocmancerConfig, load_project_config_yaml
from docmancer.core.styles import (
    CANONICAL_STYLE_NAMES,
    LOWERCASE_STYLE_NAMES,
    DEFAULT_STYLE_NAME,
)
from docmancer.core.languages import CANONICAL_LANGUAGE_NAMES


def _parse_kv_pairs(kv_list: Optional[List[str]]) -> Dict[str, str]:
    """Parse repeated key=value args into a dict. Accepts 'Key=Value' or 'Key:Value'."""
    if not kv_list:
        return {}
    out = {}
    for item in kv_list:
        if "=" in item:
            k, v = item.split("=", 1)
        elif ":" in item:
            k, v = item.split(":", 1)
        else:
            # treat as key with empty value
            k, v = item, ""
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def _parse_json_or_file(value: Optional[str]) -> Optional[Any]:
    """
    Accept either:
      - a JSON/YAML inline string: '{"a":1}' or "a: 1"
      - a path to a file containing JSON/YAML
    Returns parsed Python object or None.
    """
    if not value:
        return None
    p = Path(value)
    if p.exists():
        text = p.read_text(encoding="utf-8")
    else:
        text = value
    # try JSON first then YAML
    try:
        return json.loads(text)
    except Exception:
        try:
            return yaml.safe_load(text)
        except Exception:
            return None

def load_config(config_path: str) -> dict:
    """Loads and parses a YAML configuration file.

    Args:
        config_path (str): The path to the configuration file.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the configuration file is not a valid YAML file.
        ValueError: If the configuration file is missing required fields.
        RuntimeError: If an unexpected error occurs while loading the configuration.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    if not os.path.isfile(config_path):
        raise ValueError(f"Provided path is not a file: {config_path}")

    try:
        config = load_project_config_yaml(config_path)
        return config
    except yaml.YAMLError as e:
        raise ValueError(
            f"Error parsing YAML configuration file '{config_path}': {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while loading config '{config_path}': {e}"
        ) from e


def validate_style_case_insensitive(style_string: str) -> str:
    """
    Custom type function for argparse to validate --style argument,
    ignoring case, and returning the canonical style name.
    """
    lower_style_input = style_string.lower()

    if lower_style_input in LOWERCASE_STYLE_NAMES:
        # Find the original, correctly cased style name from STYLE_DEFINITIONS keys
        # by looking up its lowercase version.
        return next(
            (
                name
                for name in CANONICAL_STYLE_NAMES
                if name.lower() == lower_style_input
            ),
            None,
        )

    # Raise error if style is not found
    raise argparse.ArgumentTypeError(
        f"Invalid style '{style_string}'. "
        f"Allowed styles are: {', '.join(CANONICAL_STYLE_NAMES)} (case-insensitive). "
        f"Default: {DEFAULT_STYLE_NAME}"
    )


def find_and_load_config(
    start_path: Path, config_file_name: str = ".docmancer.yaml"
) -> dict:
    """
    Searches for a configuration file in the starting path and its parent directories.

    Args:
        start_path (Path): The directory to start searching from (usually current working directory).
        config_file_name (str): The name of the configuration file to look for.

    Returns:
        (config_path, dict): The path of the config file and a dictionary containing the loaded configuration, or an empty dict if not found.
    """
    current_path = start_path
    while current_path != current_path.parent:  # Loop until the root directory
        config_path = current_path / config_file_name
        if config_path.is_file():
            try:
                config_dict = load_config(config_path=config_path)
                return (config_path, config_dict)
            except Exception as e:
                print(
                    f"Warning: Could not load config file '{config_path}'. Error: {e}",
                    file=os.sys.stderr,
                )
                return (None, {})  # Return empty config if parsing fails
        current_path = current_path.parent
    print(
        f"No configuration file '{config_file_name}' found in current or parent directories."
    )
    return (None, {})  # Return empty config if no file found


def get_default(config, arg_name, fallback=None):
    """Gets the default value for a configuration argument.

    Args:
        config (dict): The configuration dictionary.
        arg_name (str): The name of the argument to retrieve.
        fallback (Any, optional): A fallback value to return if the argument is not found. Defaults to None.

    Returns:
        Any: The default value for the argument, or the fallback value if not found.
    """
    return config.get(
        arg_name.replace("-", "_"), fallback
    )  # Config keys are snake_case


def parse_args() -> DocmancerConfig:
    """Parses command line arguments and returns a DocmancerConfig object."""

    parser = argparse.ArgumentParser(
        description="Generate documentation from source code.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # CLI Argument for the configuration file
    parser.add_argument(
        "--config",
        type=str,
        default=".docmancer.yaml",
        help="Path to the YAML configuration file for LLM settings.",
    )
    # Define Arguments
    parser.add_argument(
        "--files",
        nargs="+",
        default=argparse.SUPPRESS,
        help="File paths or glob patterns (e.g., src/**/*.py)",
    )
    parser.add_argument(
        "--functions",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Function names or glob patterns to match functions to within speficied files (e.g., calculate_*). Default is all functions.",
    )
    parser.add_argument(
        "--ignore-files",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Files names or glob patterns to skip (e.g., src/**/test_*.py)",
    )
    parser.add_argument(
        "--ignore-functions",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Function names or glob patterns to skip within speficied files (e.g., _test_*)",
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        nargs="?",  # Make it optional so it can be defaulted by config
        default=argparse.SUPPRESS,
        help="Path to the root of the source code project. Defaults to current directory if not specified and no config file defines it.",
    )

    parser.add_argument(
        "--language",
        type=str,
        choices=CANONICAL_LANGUAGE_NAMES,
        default=argparse.SUPPRESS,
        help="Programming language of the source project",
    )

    parser.add_argument(
        "--style",
        type=str,
        choices=CANONICAL_STYLE_NAMES,
        default=argparse.SUPPRESS,
        help="Style of generated documentation",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Writes doc strings to specified files and functions",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Returns a message indicating which functions are undocumented",
    )
    parser.add_argument(
        "--force-all",
        action="store_true",
        default=argparse.SUPPRESS,
        help="If included, force-approves all generated documention. User will not be prompted to accept/skip/edit/etc..",
    )

    parser.add_argument(
        "--no-summary",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Skips summary generation for functions and parameters. Generates only documentation boilerplate in chosen format",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Skips functions that already appear to have a docstring.",
    )

    parser.add_argument(
        "--llm_config_mode",
        type=str,
        choices=["local", "remote"],
        default=argparse.SUPPRESS,
        help="Set whether the generator model is local or web-based",
    )

    parser.add_argument(
        "--model-local-path",
        type=str,
        default=argparse.SUPPRESS,
        help="Filepath to .gguf file for local model",
    )
    parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Logging level (overrides DOCMANCER_LOG_LEVEL env var)",
    default=None,
    )

    parser.add_argument("--remote-endpoint", 
                        help="Remote LLM API endpoint URL"
                        )
    parser.add_argument("--remote-provider", 
                        help="Remote API provider name"
                        )
    parser.add_argument("--remote-response-path", 
                        help="Where to extract response in JSON (dotted path)"
                        )
    parser.add_argument("--remote-header", 
                        action="append",
                        help="Header override (repeatable). Format: Key=Value"
                        )
    parser.add_argument("--remote-headers-json", 
                        help="JSON/YAML string or file path for headers dict"
                        )
    parser.add_argument("--remote-payload",
                        help="JSON/YAML string or file path for payload template"
                        )
    parser.add_argument("--remote-payload-file", 
                        help="alternate explicit file path for payload template"
                        )

    # Parse arguments after defaults are set
    args = parser.parse_args()
    app_config = vars(args)

    # Dictionary representation of defaults
    config = DocmancerConfig().to_dict()

    if app_config["config"] == ".docmancer.yaml":
        # Load configuration first to use its values as defaults
        # We start searching from the current working directory where the CLI is run.
        config_path, user_config = find_and_load_config(Path.cwd())
        config.update(user_config)
    else:
        # If user explicitly provided a config path
        try:
            user_config = load_config(Path(args.config))
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing configuration file '{args.config}': {e}")
            return None
        except RuntimeError as e:
            print(f"An unexpected error occurred while loading config: {e}")
            return None

        if not user_config:
            print(f"Configuration file '{args.config}' is empty.")
            return None

        # Merge explicit config over everything else
        config.update(user_config)
        config_path = args.config

    # Post-processing for boolean flags if we want config to override default.
    # For flags using action='store_true', their default is False.
    # If we want config to set them to True, we need to handle it after parsing.
    if app_config.get("write") is None and app_config.get("check") is None:
        parser.error("You must specify either --write or --check.")

    if (
        get_default(config, "force-all", False)
        and not parser.parse_known_args()[0].force_all
    ):
        app_config["force_all"] = True
    if (
        get_default(config, "no-summary", False)
        and not parser.parse_known_args()[0].no_summary
    ):
        app_config["no_summary"] = True
    if (
        get_default(config, "skip-existing", False)
        and not parser.parse_known_args()[0].skip_existing
    ):
        app_config["skip_existing"] = True
    if get_default(config, "check", False) and not parser.parse_known_args()[0].check:
        app_config["check"] = True

    # Some basic validation/coherence checks for model type
    if (
        "llm_config_mode" in app_config
        and app_config["llm_config_mode"] == "local"
        and not app_config["model_local_path"]
    ):
        parser.error("--model-local-path is required when --llm-config-mode is 'local'.")
    if (
        "llm_config_mode" in app_config
        and app_config["llm_config_mode"] == "remote"
        and not app_config["model_remote_api"]
    ):
        parser.error("--api_endpoint is required when --llm-config-mode is 'remote'.")

    # If `project_dir` is not explicitly set, derive it from config file location
    # This logic assumes `project_dir` in config is the true project root
    if "project_dir" not in config and config:
        # If config was found, assume its parent directory is the project_dir
        config["project_dir"] = str(
            Path(config_path).parent
        )  # Store config_path in a global var or return it
    else:  # Fallback if no config and no arg
        config["project_dir"] = str(Path.cwd())

    # Ensure llm_config and remote_api exist
    llm = config.setdefault("llm_config", {})
    remote = llm.setdefault("remote_api", {})

    # Merge simple overrides
    if args.remote_endpoint:
        remote["api_endpoint"] = args.remote_endpoint
    if args.remote_provider:
        remote["provider"] = args.remote_provider
    if args.remote_response_path:
        remote["response_path"] = args.remote_response_path

    # Merge headers: priority order -> CLI key=val pairs, --remote-headers-json, existing config
    headers_from_kv = _parse_kv_pairs(args.remote_header)
    headers_from_json = _parse_json_or_file(args.remote_headers_json) or {}
    # normalize existing headers
    existing_headers = remote.get("headers") or {}
    # merge: existing <- headers_from_json <- headers_from_kv  (kv wins)
    merged_headers = {**existing_headers, **(headers_from_json or {}), **headers_from_kv}
    if merged_headers:
        remote["headers"] = merged_headers

    # Merge payload template: CLI explicit payload JSON/YAML or file overrides
    payload_src = args.remote_payload_file or args.remote_payload
    payload = _parse_json_or_file(payload_src) if payload_src else None
    # if CLI provided a simple inline payload string that parsed as string, try treating as JSON/YAML anyway
    if payload is None and payload_src:
        try:
            payload = json.loads(payload_src)
        except Exception:
            try:
                payload = yaml.safe_load(payload_src)
            except Exception:
                payload = None
    if payload is not None:
        remote["payload_template"] = payload    

    if args.log_level:
        config["log_level"] = args.log_level

    # update config with args
    config.update(app_config)

    return DocmancerConfig.from_dict(config)

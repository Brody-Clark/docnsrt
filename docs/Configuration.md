# Configuring Docmancer

Docmancer supports several options for documentation generation.
*it is recommended to use the configuration file for specifying options that do not change often.*

## Arguments & Options

> [!NOTE]
> Some features are experimental or may be incomplete

| Argument / Flag            | Description                                                 | Default |
| -------------------------- | ----------------------------------------------------------- | ------- |
| `--write`                  | Writes generated strings to files                           | N/A     |
| `--config <path>`          | Path to config file                                         | `.docmancer.yaml`     |
| `--file <path>`            | Glob pattern path to a specific file to document            | `*`  |
| `--ignore-files <name...>` | Specific file names or glob pattern to ignore (space-separated list) | N/A |
| `--functions <name...>`    | Specific function names or glob pattern to target (space-separated list) | `[*]`    |
| `--ignore-functions <name...>`| Specific function names or glob pattern to ignore (space-separated list) | N/A   |
| `--project-dir <path>`     | Path to project source.                                     | Current Working Directory |
| `--language <language>`    | Language of source files.                                   | N/A |
| `--style <style>`          | Genereated docstring format: *See supported formats*        | `None`    |
| `--no-summary`  | Skips generating summary. Creates placeholder docstrings.   | N/A |
| `--force-all`    | Skips prompting for each generated docstring. Force writes to files.    | N/A |
| `--model-type <backend>`   | Type of LLM to use (local, web)                             | N/A |
| `--model-local-path <path>`| File path of .gguf file if model-type is 'local'            | N/A |
| `--model-web-api <url>`    | URL of remote model if model-type is 'web'. _Currently Unsupported_   | N/A |
| `-h, --help`               | Show help message and exit                                  | N/A     |

## Configuration File

This project supports YAML-based config files for storing options that do not need to regularly change.
See [config.yaml](../config.yaml) for a template.

### Example

YAML for Local LLM (local .gguf file)

```yml
# .docmancer.yaml
style: PEP
language: python
files:                # Files to include by pattern
  - "src/**/*.py"
functions:
  - "*"
ignore_files:         # Files to ignore by pattern
  - "**/test_*.py"     
  - "**/__init__.py"     
  - "docs/"               
  - ".git/"        
ignore_functions:     # Functions to ignore by pattern
  - "main"               
  - "__init__"
  - "test_*"
llm_config:
  mode: LOCAL         # LLM location (LOCAL or REMOTE_API)
  temperature: 0.5   
  local:
    model_path: !ENV DOCMANCER_MODEL_PATH   # Path to .gguf file (using environment variable is optional)
    n_gpu_layers: -1 
    n_ctx: 4096        
    n_batch: 512 

```

YAML for Remote LLM (RESTful API)

```yml
# .docmancer.yaml
style: PEP
language: python
files:                # Files to include by pattern
  - "src/**/*.py"
functions:
  - "*"
ignore_files:         # Files to ignore by pattern
  - "**/test_*.py"     
  - "**/__init__.py"     
  - "docs/"               
  - ".git/"        
ignore_functions:     # Functions to ignore by pattern
  - "main"               
  - "__init__"
  - "test_*"
llm_config:
  mode: REMOTE_API
  temperature: 0.5   
  remote_api:
    provider: some-llm    #   
    api_endpoint: "http://127.0.0.1:8000/v1/chat/completions" # API endpoint
    headers:        # Optional headers in the request
      Authorization: "Bearer ${vars.API_KEY}"
    payload_template: # Define the json template key-value pairs your API expects
      model: "llm-v1"
      messages: 
        - role: "user"
          content: "${prompt}"
      max_tokens: 1024
    response_path: "choices.0.message.content"  # Path in the response where the result message is located

```

## Supported Styles

> [!NOTE]
> Support for more styles is ongoing

- PEP
- XML

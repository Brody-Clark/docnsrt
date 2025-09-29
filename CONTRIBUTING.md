# Contributing

## Table of Contents

- [Contributing](#contributing)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Installing Poetry](#installing-poetry)
    - [Setting up Environment](#setting-up-environment)
  - [Code Style \& Formatting with Black](#code-style--formatting-with-black)
  - [Linting with Pylint](#linting-with-pylint)
    - [Running Pylint](#running-pylint)
    - [Fixing Lint Issues](#fixing-lint-issues)
    - [Linting Checklist](#linting-checklist)
  - [VS Code Setup](#vs-code-setup)
    - [Debugging](#debugging)
    - [Testing](#testing)
    - [Recommended Extensions](#recommended-extensions)
  - [Docstring Guidelines](#docstring-guidelines)
    - [Where to Add Docstrings](#where-to-add-docstrings)
    - [Format Example](#format-example)
  - [Unit Testing](#unit-testing)
    - [Test Directory Structure](#test-directory-structure)
    - [Writing a Test](#writing-a-test)
    - [Running Tests](#running-tests)
    - [Test Checklist](#test-checklist)
  - [Before you Commit](#before-you-commit)
  - [Branching Strategy](#branching-strategy)
    - [Creating a Feature Branch](#creating-a-feature-branch)
    - [Working on Your Branch](#working-on-your-branch)
    - [Submitting a Pull Request](#submitting-a-pull-request)
    - [Merging](#merging)

## Getting Started

### Installing Poetry

This project uses [Poetry]([Poetry](https://github.com/python-poetry/poetry)) for dependency management and virtual environments.

If you don't have Poetry installed, run:

```bash
curl -sSL https://install.python-poetry.org | python -
```

See the [Poetry installation docs](https://python-poetry.org/docs/#installing-with-pipx) for more options.

### Setting up Environment

1. Clone the repository

    ```bash
    git clone https://github.com/brody-clark/docmancer.git
    cd Docmancer
    ```

2. Install Dependencies

    ```bash
    poetry install
    ```

3. Activate the Virtual Environment

    ```bash
    poetry env activate
    ```
> [!NOTE]
> On Windows you may need to relax Powershell policies regarding script execution. To do this, you can run:
>  ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
> ```

## Code Style & Formatting with Black

- This project follows [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- All code should be formatted using [black](https://github.com/psf/black).
- Run the formatter prior to commits:

    ```bash
    black .
    ```

## Linting with Pylint

This project uses [Pylint](https://pylint.pycqa.org/) for static code analysis and enforcing code quality.

### Running Pylint

To run Pylint on your codebase, use:

```bash
poetry run pylint src
```

- This will lint all files in the `src/` directory.
- If you want to ignore specific files or folders (e.g., test projects), use the `--ignore-patterns` option:

    ```bash
    poetry run pylint --ignore-patterns='^tests/test_projects/.*' src
    ```

### Fixing Lint Issues

- Review the output and fix any reported issues before committing.
- You can disable specific warnings in your code using comments, e.g.:

    ```python
    # pylint: disable=too-few-public-methods
    ```

### Linting Checklist

- Run Pylint before submitting a pull request.
- Ensure your code passes with minimal warnings.
- Address any critical errors or code style issues.

**Tip:**  
Add Pylint as a dev dependency with:

```bash
poetry add --dev pylint
```

## VS Code Setup

This project includes recommended VS Code configurations for debugging and testing.

### Debugging

- Use the provided launch configurations in `.vscode/launch.json` to debug:
  - Test project files
  - Individual unit test files with pytest
  - Any file with the Poetry environment

To start debugging, open the Run & Debug sidebar and select the desired configuration.

### Testing

- Tests are discovered and run using pytest, as configured in `.vscode/settings.json`.
- You can run and debug tests from the Testing sidebar or using the "Debug: pytest Current File" launch configuration.

### Recommended Extensions

- Python
- Pylint
- Black
- pytest

## Docstring Guidelines

This project follows [PEP 257-style](https://peps.python.org/pep-0257/) docstrings with an emphasis on clarity and brevity.

### Where to Add Docstrings

| Element                    | Docstring Required? | Notes                                            |
| -------------------------- | ------------------- | ------------------------------------------------ |
| Public modules             | Yes                 | Brief summary of purpose                         |
| Public classes             | Yes                 | Summary and responsibilities                     |
| Public methods/functions   | Yes                 | Summary, parameter descriptions, and return info |
| Private/internal functions | Optional            | Add only if they are complex                     |
| Test functions             | No                  | Prefer self-documenting names                    |

### Format Example

```py
def normalize_data(data: List[float]) -> List[float]:
    """
    Normalize a list of floats to the 0–1 range.

    Args:
        data (List[float]): The list of values to normalize.

    Returns:
        List[float]: Normalized values between 0 and 1.
    """
```

## Unit Testing

This project uses [pytest](https://docs.pytest.org/en/stable/) for all unit testing.

### Test Directory Structure

All tests should go in the `tests/` directory and mirror the structure of the src/ folder:

```pqsql
project-root/
├── src/
│   └── core/
│       └── parser/
│           └── python_parser.py
└── tests/
    └── core/
        └── parser/
            └── test_python_parser.py
```

### Writing a Test

- Test files should be named test_*.py.

- Test functions should begin with test_.

- Use clear, descriptive function names.

- Prefer unit tests (isolated and fast), but integration tests are welcome if scoped properly.

```py
# tests/core/parser/test_python_parser.py

import pytest
from core.parser.python_parser import extract_function_signature

def test_extract_function_signature_returns_expected_signature():
    source_code = "def add(a, b):\n    return a + b"
    result = extract_function_signature(source_code)
    assert result == "def add(a, b):"
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/core/parser/test_python_parser.py
```

Run tests and display code coverage (optional):

```bash
pytest --cov=src
```

**Make sure to install test dependencies:**

```bash
poetry install --with dev
```

### Test Checklist

- Does each function/module have corresponding tests?
- Do your tests cover edge cases?
- Do your tests fail when the code is broken?
- Are tests isolated (i.e. no hidden dependencies)?
- Is your test data simple and self-explanatory?

## Before you Commit

1. Format your code
2. Run tests if possible
3. Keep commits small and focused.
4. Write clear commit messages using the conventional format:

    ```txt
    feat: Add support for --function argument
    fix: Correct line offset handling in parser
    chore: refactored python parser
    ```

## Branching Strategy

This project uses a simple branching model to keep development organized and stable.

- **main**: The stable release branch. Only thoroughly tested code is merged here.
- **dev**: The active development branch. All new features, bug fixes, and changes are merged into dev before being promoted to main.
- **feature branches**: For new features, improvements, or bug fixes. These branches should be created from dev and merged back into dev via Pull Request.

### Creating a Feature Branch

1. Make sure you are up to date with the dev branch:

    ```bash
    git checkout dev
    git pull origin dev
    ```

2. Create your feature branch:

    ```bash
    git checkout -b feat/my-new-feature
    ```

    Use a descriptive name for your branch, prefixed with `feat/`, `fix/`, or `chore/` as appropriate.

### Working on Your Branch

- Commit your changes regularly.
- Push your branch to the remote repository:

    ```bash
    git push -u origin feat/my-new-feature
    ```

### Submitting a Pull Request

- When your work is ready, open a Pull Request (PR) **from your feature branch into dev**.
- Fill out the PR template and describe your changes clearly.
- Ensure your branch passes all tests and code style checks before requesting a review.

### Merging

- Feature branches are merged into dev after review and approval.
- Periodically, dev is merged into main for releases.

**Summary:**

- Always branch off dev.
- Always merge feature branches into dev via Pull Request.
- Do not commit directly to main or dev unless performing a release or hotfix.

# Installing docnsrt

## Prerequisites

- Python 3.8+
- Poetry (for dependency and environment management)

Install Poetry if you haven't already:
```bash
pip install poetry
```

## Installation Steps

1. Clone the Repository
    ```bash
    git clone https://github.com/brody-clark/docnsrt.git
    cd docnsrt
    ```
2. Install Dependencies
    ```bash
    poetry install
    ```
3. Test the Tool (Optional)
    ```bash
    poetry run docnsrt --help
    ```
4. Install as a Global CLI Tool
    ```bash
    poetry install --with main
    poetry build
    poetry install --no-root
    ```
5. Confirm Installation
    ```bash
    docnsrt --help
    ```

## Uninstallation

To remove the tool:
```bash
poetry env remove python 
```
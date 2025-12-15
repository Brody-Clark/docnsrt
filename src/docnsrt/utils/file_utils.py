"""Utilities for file operations."""

import os
from pathlib import Path
from typing import List
import fnmatch


def get_all_files_in_dir(dir_path):
    """
    Returns a list of all files in the given directory path.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list: A list of file names in the directory.
            Returns an empty list if the directory does not exist or is empty.
    """
    if not os.path.isdir(dir_path):
        return []

    files = os.listdir(dir_path)
    return files


def get_files_by_pattern(
    start_dir: str,
    include_patterns: List[str],
    ignore_patterns: List[str],
    extensions: List[str],
) -> List[Path]:
    """
    Return a list of Path objects matching the given glob pattern and extensions,
    starting from the specified directory. Ignores files matching any of the ignore patterns.
    Example patterns:
        "*.py" - all Python files in current dir
        "src/**/*.py" - all Python files recursively under src/
    """
    start = Path(start_dir)
    matches = set()

    # Find all files matching include patterns
    for include_pattern in include_patterns:
        for fn in start.glob(include_pattern):
            # Filter out ignored patterns
            if any(fn.match(ignore_pattern) for ignore_pattern in ignore_patterns):
                continue
            matches.add(fn)

    # Filter by extensions
    if extensions:
        matches = {
            fn for fn in matches if any(fn.name.endswith(ext) for ext in extensions)
        }

    return list(matches)


def get_line_text_offset_spaces(file_path: str, line: int) -> int:
    """
    Returns the number of spaces before text begins on a given line
    or -1 if not found.

    Args:
        line (int): line number of file

    """
    with open(file_path, "r", encoding="utf8") as f:
        for idx, line_text in enumerate(f, start=0):
            if idx == line:
                return len(line_text) - len(line_text.lstrip(" "))
    return -1


def read_file_to_string(file_path):
    """Returns content of a file as a string.

    Args:
        file_path (str): path to file

    Returns:
        str: content of file as string
    """
    with open(file_path, "r", encoding="utf8") as file:
        file_content = file.read()
        return file_content


def read_file_to_bytes(file_path):
    """Returns content of a file as bytes.

    Args:
        file_path (file_path): path to file

    Returns:
        bytes: content of file in bytes
    """
    with open(file_path, "rb") as file:
        file_content = file.read()
        return file_content

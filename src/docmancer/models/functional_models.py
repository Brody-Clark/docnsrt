"""Model for function summaries."""

from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ParameterModel:
    """Model for function parameters."""

    name: str
    type: str
    desc: str


@dataclass_json
@dataclass
class ExceptionModel:
    """Model for function exceptions."""

    type: str
    desc: str


@dataclass_json
@dataclass
class DocstringModel:
    """Model for function docstrings."""

    lines: List[str]
    start_line: int

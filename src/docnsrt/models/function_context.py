"""
Model for function context information.
"""

from dataclasses import dataclass
from typing import List
from docnsrt.models.functional_models import ParameterModel, DocstringModel

@dataclass
class FunctionContextModel:
    """Model for function context information."""

    qualified_name: str
    signature: str
    parameters: List[ParameterModel]
    docstring: DocstringModel
    start_line: int

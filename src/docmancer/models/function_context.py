"""
Model for function context information.
"""

from dataclasses import dataclass
from typing import List
from docmancer.models.functional_models import ParameterModel, DocstringModel


@dataclass
class FunctionContextModel:
    """Model for function context information."""

    qualified_name: str
    signature: str
    return_type: str
    parameters: List[ParameterModel]
    docstring: DocstringModel
    body: str
    start_line: int
    end_line: int

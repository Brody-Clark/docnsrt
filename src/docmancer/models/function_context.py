from dataclasses import dataclass
from typing import List
from docmancer.models.functional_models import ParameterModel


@dataclass
class FunctionContextModel:
    qualified_name: str
    signature: str
    return_type: str
    parameters: List[ParameterModel]
    body: str
    comments: List[str]
    start_line: int
    end_line: int

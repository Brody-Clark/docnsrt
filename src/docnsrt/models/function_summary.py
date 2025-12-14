"""Model for function summaries."""

from typing import List, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from docnsrt.models.functional_models import ParameterModel, ExceptionModel


@dataclass_json
@dataclass
class FunctionSummaryModel:
    """Model for function summaries returned by the documentation generator."""

    summary: str
    return_description: Optional[str] = None
    parameters: List[ParameterModel] = field(default_factory=list)
    return_type: Optional[str] = None
    exceptions: List[ExceptionModel] = field(default_factory=list)
    remarks: Optional[str] = None

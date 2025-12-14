"""This module provides function summary generators"""

import logging
from abc import abstractmethod, ABC
from docnsrt.models.functional_models import ExceptionModel, ParameterModel
import docnsrt.utils.json_utils as ju
from docnsrt.models.function_context import FunctionContextModel
from docnsrt.models.function_summary import FunctionSummaryModel

logger = logging.getLogger(__name__)


class GeneratorBase(ABC):
    @abstractmethod
    def get_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:
        """Creates a function summary model based on function context

        Args:
            context (FunctionContextModel): Function context

        Returns:
            FunctionSummaryModel: Model containing information for docstring creation
        """


class DocstringGenerator(GeneratorBase):
    """
    Default implementation of the function summary generator.
    Provides no summary, only placeholders.
    """

    def __init__(self):
        pass

    # TODO: generate template fields for all parameters and exceptions
    def get_summary(self, context: FunctionContextModel) -> FunctionSummaryModel:
        return FunctionSummaryModel(
            summary="_summary_",
            return_description="_returns_",
            return_type="_return_type_",
            remarks="_remarks_",
            exceptions=[ExceptionModel(type="_type_", desc="_description_")],
            parameters=[
                ParameterModel(name="_name_", type="_type_", desc="_description_")
            ],
        )

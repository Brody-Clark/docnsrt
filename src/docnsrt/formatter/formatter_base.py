"""Base class for all formatters."""

from abc import abstractmethod, ABC
from docnsrt.models.function_context import FunctionContextModel
from docnsrt.models.function_summary import FunctionSummaryModel
from docnsrt.models.formatted_summary_model import FormattedSummaryModel


class FormatterBase(ABC):
    """
    Base class for all formatters.
    """

    @abstractmethod
    def get_formatted_documentation(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        func_summary: FunctionSummaryModel,
    ) -> FormattedSummaryModel:
        """
        Creates a formatted documentation model that can be used to write a docstring into a source file.

        Args:
            doc_model: Generated documentation response model object

        Returns:
            A formatted Python docstring string.
        """

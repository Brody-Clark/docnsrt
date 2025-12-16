"""Base class for all formatters."""

from abc import abstractmethod, ABC
from docnsrt.core.models import (
    FunctionContextModel,
    DocstringTemplateModel,
    FormattedDocstringModel,
)


class FormatterBase(ABC):
    """
    Base class for all formatters.
    """

    @abstractmethod
    def get_formatted_docstring(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        template_values: DocstringTemplateModel,
    ) -> FormattedDocstringModel:
        """
        Creates a formatted documentation model that can be used to write a docstring into a source file.

        Args:
            doc_model: Generated documentation response model object

        Returns:
            A formatted Python docstring string.
        """

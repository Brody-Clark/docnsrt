"""This module provides function summary generators"""

import logging
from docnsrt.core.models import (
    DocstringTemplateModel,
    ExceptionModel,
    ParameterModel,
    FunctionContextModel,
)

logger = logging.getLogger(__name__)


class DocstringGenerator:
    """
    Default implementation of the function summary generator.
    Provides no summary, only placeholders.
    """

    def __init__(self):
        pass

    def get_template_values(
        self, context: FunctionContextModel
    ) -> DocstringTemplateModel:
        """Generates template values for a given function context."""
        return DocstringTemplateModel(
            summary="_summary_",
            return_description="_desc_",
            return_type="_type_",
            remarks="_remarks_",
            exceptions=[ExceptionModel(type="_type_", desc="_desc_")],
            parameters=[
                ParameterModel(name=p.name, type=p.type, desc="_desc_")
                for p in context.parameters
            ],
        )

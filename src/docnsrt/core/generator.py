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

    # TODO: generate template fields for all parameters and exceptions
    def get_template_values(
        self, context: FunctionContextModel
    ) -> DocstringTemplateModel:
        return DocstringTemplateModel(
            summary="_summary_",
            return_description="_returns_",
            return_type="_return_type_",
            remarks="_remarks_",
            exceptions=[ExceptionModel(type="_type_", desc="_description_")],
            parameters=[
                ParameterModel(name="_name_", type="_type_", desc="_description_")
            ],
        )

"""Formatters for Python code."""

from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.core.models import (
    DocstringLocation,
    FormattedDocstringModel,
    DocstringTemplateModel,
    FunctionContextModel,
)
import docnsrt.utils.file_utils as fu

INDENT_SPACES = 4


class PythonPepFormatter(FormatterBase):
    """
    Formats Python docstrings according to PEP 257.
    """

    def get_formatted_docstring(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        template_values: DocstringTemplateModel,
    ) -> FormattedDocstringModel:

        function_signature_offset = fu.get_line_text_offset_spaces(
            file_path, func_context.start_line
        )

        lines = ['"""', template_values.summary.strip(), ""]

        if template_values.parameters:
            lines.append("Args:")
            for param in template_values.parameters:
                name = param.name
                typ = param.type if param.type is not None else "Any"
                desc = param.desc
                lines.append(f"    {name} ({typ}): {desc}")

        if template_values.return_description:
            lines.append("")
            lines.append("Returns:")
            lines.append(f"    {template_values.return_description.strip()}")

        lines.append('"""')

        # add newlines to each line
        lines = [line + "\n" for line in lines]

        if function_signature_offset >= 0:
            offset = function_signature_offset + INDENT_SPACES
        else:
            raise ValueError(
                f"Unable to read start line {func_context.start_line} from file {file_path}"
            )

        doc_model = FormattedDocstringModel(
            formatted_documentation=lines,
            start_line=func_context.start_line
            + 1,  # pep doc strings go right below the signature
            offset_spaces=offset,
            docstring_location=DocstringLocation.BELOW,
        )

        return doc_model

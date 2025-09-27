"""Formatters for Python code."""

from docmancer.models.formatted_summary_model import FormattedSummaryModel
from docmancer.formatter.formatter_base import FormatterBase
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.docstring_models import DocstringLocation

import docmancer.utils.file_utils as fu

INDENT_SPACES = 4


class PythonPepFormatter(FormatterBase):
    """
    Formats Python docstrings according to PEP 257.
    """

    def get_formatted_documentation(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        func_summary: FunctionSummaryModel,
    ) -> FormattedSummaryModel:

        function_signature_offset = fu.get_line_text_offset_spaces(
            file_path, func_context.start_line
        )

        lines = ['"""', func_summary.summary.strip(), ""]

        if func_summary.parameters:
            lines.append("Args:")
            for param in func_summary.parameters:
                name = param.name
                typ = param.type if param.type is not None else "Any"
                desc = param.desc
                lines.append(f"    {name} ({typ}): {desc}")

        if func_summary.return_description:
            lines.append("")
            lines.append("Returns:")
            lines.append(f"    {func_summary.return_description.strip()}")

        lines.append('"""')

        # add newlines to each line
        lines = [line + "\n" for line in lines]

        if function_signature_offset >= 0:
            offset = function_signature_offset + INDENT_SPACES
        else:
            raise ValueError(
                f"Unable to read start line {func_context.start_line} from file {func_context.file_path}"
            )

        doc_model = FormattedSummaryModel(
            formatted_documentation=lines,
            start_line=func_context.start_line + 1,  # pep doc strings go right below the signature
            offset_spaces=offset,
            docstring_location=DocstringLocation.BELOW,
        )

        return doc_model

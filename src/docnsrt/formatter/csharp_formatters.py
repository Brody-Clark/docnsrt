"""Formatters for C# docstrings."""

from docnsrt.core.models import DocstringLocation
import docnsrt.utils.file_utils as fu
from docnsrt.core.models import FunctionContextModel
from docnsrt.core.models import DocstringTemplateModel
from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.core.models import FormattedDocstringModel

COMMENT_START = "/// "


class CSharpXmlFormatter(FormatterBase):
    """Formatter for C# XML documentation comments."""

    def get_formatted_docstring(
        self,
        file_path: str,
        func_context: FunctionContextModel,
        template_values: DocstringTemplateModel,
    ) -> FormattedDocstringModel:
        function_signature_offset = fu.get_line_text_offset_spaces(
            file_path, func_context.start_line
        )

        lines = [
            COMMENT_START + "<summary>",
            COMMENT_START + template_values.summary.strip(),
            COMMENT_START + "</summary>",
        ]

        if template_values.parameters:
            for param in template_values.parameters:
                name = param.name
                desc = param.desc
                lines.append(COMMENT_START + f"<param name=\"{name}\">{desc}</param>")

        if template_values.return_description:
            lines.append(
                COMMENT_START
                + f"<returns>{template_values.return_description}</returns>"
            )

        # Add newlines to each line
        lines = [line + "\n" for line in lines]

        if function_signature_offset >= 0:
            offset = function_signature_offset
        else:
            raise ValueError(
                f"Unable to read start line {func_context.start_line} from file {file_path}"
            )

        formatted_summary = FormattedDocstringModel(
            formatted_documentation=lines,
            start_line=func_context.start_line,  # XML comments go right above the signature
            offset_spaces=offset,
            docstring_location=DocstringLocation.ABOVE,
        )

        return formatted_summary

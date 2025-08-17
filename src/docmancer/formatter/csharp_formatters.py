import docmancer.utils.file_utils as fu
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.documentation_model import DocumentationModel
from docmancer.formatter.formatter_base import FormatterBase
from docmancer.models.formatted_summary_model import FormattedSummaryModel

COMMENT_START = "/// "


class CSharpXmlFormatter(FormatterBase):

    def get_formatted_documentation(
        self,
        func_context: FunctionContextModel,
        func_summary: FunctionSummaryModel
    ) -> FormattedSummaryModel:
        function_signature_offset = fu.get_line_text_offset_spaces(
            func_context.file_path, func_context.start_line
        )

        lines = [
            COMMENT_START + "<summary>",
            COMMENT_START + func_summary.summary.strip(),
            COMMENT_START + "</summary>",
        ]

        if func_summary.parameters:
            for param in func_summary.parameters:
                name = param.name
                desc = param.desc
                lines.append(COMMENT_START + f"<param name=\"{name}\">{desc}</param>")

        if func_summary.return_description:
            lines.append(
                COMMENT_START + f"<returns>{func_summary.return_description}</returns>"
            )

        # Add newlines to each line
        lines = [line + "\n" for line in lines]

        if function_signature_offset >= 0:
            offset = function_signature_offset
        else:
            raise ValueError(
                f"Unable to read start line {func_context.start_line} from file {func_context.file_path}"
            )

        doc_model = FormattedSummaryModel(
            formatted_documentation=lines,
            start_line=func_context.start_line - 1,
            offset_spaces=offset,
        )

        return doc_model

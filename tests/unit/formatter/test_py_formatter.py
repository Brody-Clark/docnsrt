import unittest
from unittest.mock import patch
from docnsrt.formatter.python_formatters import PythonPepFormatter
from docnsrt.core.models import (
    DocstringTemplateModel,
    DocstringModel,
    FunctionContextModel,
)


class TestPepFormatter(unittest.TestCase):

    @patch("docnsrt.formatter.python_formatters.fu.get_line_text_offset_spaces")
    def test_get_formatted_documentation(self, mock_get_line_text_offset_spaces):

        # mock return 4 spaces (tab)
        mock_get_line_text_offset_spaces.return_value = 4

        formatter = PythonPepFormatter()
        test_func_context = FunctionContextModel(
            qualified_name="test.class.func",
            signature="def func()",
            parameters=[],
            start_line=1,
            docstring=DocstringModel(lines=[], start_line=2),
        )
        test_func_summary = DocstringTemplateModel(
            summary="this is a test function",
            return_description="returns nothing",
            parameters=[],
        )
        test_doc_model = formatter.get_formatted_docstring(
            file_path="test_file.py",
            func_context=test_func_context,
            template_values=test_func_summary,
        )

        expected_docstring = [
            '"""\n',
            "this is a test function\n",
            "\n",
            "\n",
            "Returns:\n",
            "    returns nothing\n",
            '"""\n',
        ]

        assert (
            test_doc_model.offset_spaces == 8
        )  # must be a tab (4) added to existing (provided by mock)
        assert (
            test_doc_model.start_line == 2
        )  # pep docstrings go right below the signature
        assert test_doc_model.formatted_documentation == expected_docstring

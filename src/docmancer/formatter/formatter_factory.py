"""
Formatter factory for creating formatter instances.
"""

from docmancer.formatter.formatter_base import FormatterBase
from docmancer.formatter.python_formatters import PythonPepFormatter
from docmancer.formatter.csharp_formatters import CSharpXmlFormatter
from docmancer.core.styles import DocstringStyle
from docmancer.core.languages import Languages


class FormatterFactory:
    """
    Factory class for creating formatters.
    """

    def get_formatter(self, style: str, language: str) -> FormatterBase:
        """
        Returns a formatter instance based on the specified style and language.

        Args:
            style (str): The docstring style to use.
            language (str): The programming language of the code.

        Returns:
            FormatterBase: An instance of a formatter for the specified style and language.
        """
        if language == Languages.PYTHON.value:
            if style.lower() == DocstringStyle.PEP.lower():
                return PythonPepFormatter()
        if language == Languages.CSHARP.value:
            if style.lower() == DocstringStyle.XML.lower():
                return CSharpXmlFormatter()
        raise ValueError(f"Unsupported style '{style}' for language '{language}'")

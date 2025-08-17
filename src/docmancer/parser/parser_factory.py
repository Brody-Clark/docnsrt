"""Factory for creating parsers for different programming languages."""

from docmancer.parser.parser_base import ParserBase
from docmancer.parser.python_parser import PythonParser
from docmancer.parser.csharp_parser import CSharpParser


class ParserFactory:
    """
    Factory for creating parsers for different programming languages.
    """

    def get_parser(self, language: str) -> ParserBase:
        """
        Returns a parser for the specified programming language.

        Args:
            language (str): The programming language to create a parser for.

        Returns:
            ParserBase: An instance of a parser for the specified language.
        """
        if language == "python":
            return PythonParser()
        if language == "csharp":
            return CSharpParser()

        return None

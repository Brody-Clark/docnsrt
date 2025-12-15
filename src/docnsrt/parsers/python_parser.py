"""Parser for Python code."""

import logging
from typing import List
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from docnsrt.core.models import ParameterModel, DocstringModel, FunctionContextModel
from docnsrt.parsers.parser_base import ParserBase

logger = logging.get_logger(__name__)


class PythonParser(ParserBase):
    """
    Parser for Python code.
    """

    def __init__(self):
        ParserBase.__init__(self)
        self._language = Language(tspython.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
        function_definition
            name: (identifier) @func.name
        )
        """

    def get_parameters(self, parameters_node, source_code) -> List:
        """Extracts parameters from a function definition node.

        Args:
            parameters_node (tree_sitter.Node): The parameters node to extract information from.
            source_code (str): The source code as a string.

        Returns:
            List: A list of ParameterModel instances representing the function parameters.
        """
        parameters = []
        for child in parameters_node.children:
            if child.type == "parameter":
                param_name = self.get_node_text(
                    child.child_by_field_name("name"), source_code
                )
                param_type = self.get_node_text(
                    child.child_by_field_name("type"), source_code
                )
                parameters.append(
                    ParameterModel(name=param_name, type=param_type, desc="")
                )
        return parameters

    def get_qualified_name(self, node, source_code: str) -> str:
        """Get the qualified name of the function, including class and module names.

        Args:
            node (tree_sitter.Node): The function definition node.
            source_code (str): The source code as a string.
        Returns:

            str: The qualified name of the function.
        """
        qualified_name = self.get_node_text(
            node.child_by_field_name("name"), source_code=source_code
        )
        parent = node.parent
        while parent is not None:
            if parent.type == "class_definition":
                class_name_node = parent.child_by_field_name("name")
                class_name = self.get_node_text(
                    class_name_node, source_code=source_code
                )
                qualified_name = (
                    f"{class_name}.{qualified_name}" if qualified_name else class_name
                )
            elif parent.type == "module":
                # Assuming module name is derived from file name or provided context
                break
            parent = parent.parent
        return qualified_name

    def get_name(self, root_node, source_code: str) -> str:
        """Returns the name of the given node or empty string."""
        name_node = root_node.child_by_field_name("name")
        if not name_node:
            logger.warn("Invalid name node")
            return ""
        name = self.get_node_text(name_node, source_code=source_code)
        return name

    def get_docstring(self, block_node, source_code: str) -> DocstringModel:
        """Creates a docstring model from a body node"""
        first_stmt = block_node.child(0)
        if first_stmt and first_stmt.type == "expression_statement":
            expr = first_stmt.child(0)
            if expr and expr.type == "string":
                # Get the text slice from the original source
                comment = self.get_node_text(expr, source_code)
                return DocstringModel(
                    lines=comment.splitlines(), start_line=expr.start_point[0]
                )
        return None

    def extract_function_context(
        self, root_node, source_code: str, module_name: str
    ) -> FunctionContextModel:
        """Extracts function context from a function definition node."""

        if root_node is None or root_node.type != "function_definition":
            raise ValueError("Provided root_node is not a function_definition node.")

        name = self.get_name(root_node, source_code)
        parameters_node = root_node.child_by_field_name("parameters")
        signature = (
            f"def {name}{self.get_node_text(parameters_node, source_code=source_code)}"
        )
        parameters = self.get_parameters(parameters_node, source_code)

        block_node = root_node.child_by_field_name("body")
        docstring = None
        if block_node:
            docstring = self.get_docstring(block_node, source_code)

        qualified_name = name
        while root_node is not None:
            if root_node.type == "class_definition":
                class_name_node = root_node.child_by_field_name("name")
                class_name = self.get_node_text(
                    class_name_node, source_code=source_code
                )
                qualified_name = (
                    f"{class_name}.{qualified_name}" if qualified_name else class_name
                )
            elif root_node.type == "module":
                qualified_name = (
                    f"{module_name}.{qualified_name}" if qualified_name else module_name
                )
                break
            root_node = root_node.parent

        context = FunctionContextModel(
            qualified_name=qualified_name,
            parameters=parameters,
            signature=signature,
            docstring=docstring,
            start_line=root_node.start_point[0],
        )
        return context

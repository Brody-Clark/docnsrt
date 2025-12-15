"""Parser for Python code."""

from typing import List
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from docnsrt.core.models import ParameterModel, DocstringModel, FunctionContextModel
from docnsrt.parsers.parser_base import ParserBase


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

    def extract_function_context(
        self, root_node, source_code: str, module_name: str
    ) -> FunctionContextModel:

        node_stack = [(root_node, [])]  # (node, scope_stack)

        while node_stack:
            node, scope = node_stack.pop()

            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                name = self.get_node_text(name_node, source_code=source_code)
                new_scope = scope + [name]
                qualified_name = ".".join([module_name] + new_scope)

                parameters_node = node.child_by_field_name("parameters")
                signature = f"def {name}{self.get_node_text(parameters_node, source_code=source_code)}"

                block_node = node.child_by_field_name("body")
                if not block_node:
                    continue
                docstring = None
                first_stmt = block_node.child(0)
                if first_stmt and first_stmt.type == "expression_statement":
                    expr = first_stmt.child(0)
                    if expr and expr.type == "string":
                        # Get the text slice from the original source
                        comment = self.get_node_text(expr, source_code)
                        docstring = DocstringModel(
                            lines=comment.splitlines(), start_line=expr.start_point[0]
                        )

                parameters = self.get_parameters(parameters_node, source_code)

                context = FunctionContextModel(
                    qualified_name=qualified_name,
                    parameters=parameters,
                    signature=signature,
                    docstring=docstring,
                    start_line=node.start_point[0],
                )
                return context

            else:
                # Add children to stack (depth-first traversal)
                for child in reversed(node.children):
                    node_stack.append((child, scope))
        return None

"""Parser for the C# language."""

from typing import List
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser
from docnsrt.parsers.parser_base import ParserBase
from docnsrt.models.function_context import FunctionContextModel
from docnsrt.models.functional_models import ParameterModel, DocstringModel


class CSharpParser(ParserBase):
    """Parser for C# code.

    Args:
        ParserBase (ParserBase): Base parser class.
    """

    def __init__(self):
        ParserBase.__init__(self)
        self._language = Language(tscsharp.language())
        self._parser = Parser(self._language)
        self._query_str = """
        (
        method_declaration
            name: (identifier) @func.name
        )
        """

    def get_enclosing_class_name(self, node, source_code):
        """Get the name of the class enclosing the given node.

        Args:
            node (tree_sitter.Node): The node to check.
            source_code (str): The source code being parsed.

        Returns:
            str: The name of the enclosing class, or None if not found.
        """
        parent = node.parent
        while parent is not None:
            if parent.type == "class_declaration":
                # The class name is usually an 'identifier' child of the class_declaration
                for child in parent.children:
                    if child.type == "identifier":
                        return source_code[child.start_byte : child.end_byte]
            parent = parent.parent
        return None

    def get_parameters(self, parameters_node, source_code) -> List[ParameterModel]:
        """Extract parameters from a parameter list node.

        Args:
            parameters_node (tree_sitter.Node): The start of the parameter tree
            source_code (str): The source code being parsed

        Returns:
            List[ParameterModel]: A list of extracted parameters
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

    def extract_function_contexts(
        self, root_node, source_code, module_name
    ) -> List[FunctionContextModel]:

        function_contexts = []
        node_stack = [(root_node, [])]  # (node, scope_stack)

        while node_stack:
            node, scope = node_stack.pop()

            if node.type == "method_declaration":
                return_type = None
                identifiers = []
                modifiers = []
                parameters_node = None
                for child_node in node.children:
                    if child_node.type == "modifier":
                        modifiers.append(
                            self.get_node_text(child_node, source_code=source_code)
                        )
                    elif child_node.type == "parameter_list":
                        parameters_node = child_node
                    elif child_node.type == "predefined_type":
                        return_type = self.get_node_text(
                            child_node, source_code=source_code
                        )
                    elif child_node.type == "identifier":
                        identifiers.append(
                            self.get_node_text(child_node, source_code=source_code)
                        )

                docstring = None
                prev_sibling = node.prev_sibling
                if prev_sibling is not None and prev_sibling.type == "comment":
                    comment = self.get_node_text(prev_sibling, source_code=source_code)
                    docstring = DocstringModel(
                        lines=comment.splitlines(),
                        start_line=prev_sibling.start_point[0],
                    )

                modifiers_str = " ".join(modifiers) if modifiers else ""
                identifiers_str = " ".join(identifiers) if identifiers else ""
                return_type = f" {return_type} " if return_type is not None else ""
                parameters_str = self.get_node_text(
                    parameters_node, source_code=source_code
                )
                signature = (
                    f"{modifiers_str}{return_type}{identifiers_str}{parameters_str}"
                )
                parameters = self.get_parameters(parameters_node, source_code)

                function_contexts.append(
                    FunctionContextModel(
                        qualified_name=".".join([module_name] + scope + identifiers),
                        signature=signature,
                        parameters=parameters,
                        docstring=docstring,
                        start_line=node.range.start_point.row,
                    )
                )
            elif node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                class_name = self.get_node_text(name_node, source_code=source_code)
                new_scope = scope + [class_name]
                for child in reversed(node.children):
                    node_stack.append((child, new_scope))

            else:
                for child in reversed(node.children):
                    node_stack.append((child, scope))

        return function_contexts

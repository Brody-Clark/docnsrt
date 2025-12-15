"""Base class for all parsers."""

import logging
from abc import ABC, abstractmethod
from typing import List
import os
import fnmatch
import docnsrt.utils.file_utils as fu
from docnsrt.core.models import FunctionContextModel

logger = logging.getLogger(__name__)


class ParserBase(ABC):
    """
    Base class for all parsers.
    """

    def __init__(self):
        self._language = None
        self._parser = None
        self._query_str = None

    def get_function_nodes(self, tree):
        """
        Retrieves function nodes from the parse tree.
        """
        query = self._language.query(self._query_str)
        captures = query.captures(tree.root_node)
        return captures

    def get_function_names(self, captures, source_code: bytes) -> dict:
        """Retrieves function names from the capture groups.

        Args:
            captures (_type_): _description_
            source_code (bytes): _description_

        Returns:
            dict: _description_
        """

        func_nodes = {}
        for capture_name in captures:
            if capture_name == "func.name":
                for node in captures[capture_name]:
                    func_name = source_code[node.start_byte : node.end_byte].decode(
                        "utf-8"
                    )
                    func_nodes[node] = func_name
        return func_nodes

    def filter_functions(
        self,
        tree,
        source_code: bytes,
        include_pattern: List[str],
        ignore_patterns: List[str],
    ) -> List[any]:
        """Locates functions from source code based on include/ignore filters.

        Args:
            tree (Tree): tree-sitter tree
            source_code (bytes): raw source code as bytes
            include_pattern (List[str]): list of glob patterns to filter in
            ignore_patterns (List[str]): list of glob patterns to filter out

        Returns:
            List[any]: List of function nodes that pass the filters
        """
        captures = self.get_function_nodes(tree)
        matches = []
        func_nodes = self.get_function_names(
            captures=captures, source_code=source_code
        ).items()
        for node, func_name in func_nodes:
            # skip functions that dont match any include patterns
            if not any(
                fnmatch.fnmatch(func_name, pattern) for pattern in include_pattern
            ):
                continue

            # skip functions that match any ignore patterns
            if any(fnmatch.fnmatch(func_name, pattern) for pattern in ignore_patterns):
                continue

            matches.append(node.parent)  # node.parent is the full function node

        return matches

    def parse(
        self, file: str, include_patterns: List[str], ignore_patterns: List[str]
    ) -> List[FunctionContextModel]:
        """Parses a file and extracts function contexts.

        Args:
            file (str): The path to the file to parse.
            include_patterns (List[str]): Patterns to include.
            ignore_patterns (List[str]): Patterns to ignore.

        Returns:
            List[FunctionContextModel]: A list of function contexts.
        """
        try:
            code = fu.read_file_to_bytes(file.absolute())
            module_name = os.path.splitext(os.path.basename(file.absolute()))[0]
        except OSError as e:
            logger.exception(f"Error reading file {file}: {e}")
            return None
        tree = self._parser.parse(code)
        nodes = self.filter_functions(tree, code, include_patterns, ignore_patterns)
        function_nodes = set()
        function_nodes.update(nodes)
        functions = {}
        functions[module_name] = function_nodes

        # Parse each function root node and create function contexts
        function_contexts = []
        for name, function_nodes in functions.items():
            for node in function_nodes:
                function_contexts.append(
                    self.extract_function_context(node, code, name)
                )

        return function_contexts

    def get_node_text(self, node, source_code) -> str:
        """Retrieves the text content of a node from the source code.

        Args:
            node (tree_sitter.Node): The node to retrieve text from.
            source_code (bytes): The raw source code as bytes.

        Returns:
            str: The text content of the node.
        """
        return source_code[node.start_byte : node.end_byte].decode("utf-8")

    @abstractmethod
    def extract_function_context(
        self, root_node, source_code: str, module_name: str
    ) -> FunctionContextModel:
        """Extracts function context from function root node.

        Args:
            root_node (tree_sitter.Node): tree sitter root node
            source_code (str): raw source code
            module_name (str): name of the module the code belongs to

        Returns:
            FunctionContextModel: A function context or None.
        """

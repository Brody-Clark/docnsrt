import code
import pytest
from tree_sitter import Parser, Language
import tree_sitter_python as tspython
from docnsrt.core.models import FunctionContextModel
from docnsrt.parsers.python_parser import PythonParser


@pytest.fixture
def parser():
    return PythonParser()


@pytest.fixture
def get_root_node():
    def _get_root_node(source_code: bytes):
        _parser = Parser(Language(tspython.language()))
        tree = _parser.parse(source_code)
        return tree.root_node

    return _get_root_node


def test_extract_simple_function(parser, get_root_node):
    code = b"""
def foo(x, y):
    return x + y
"""
    root_node = get_root_node(code)
    context = parser.extract_function_context(root_node, code, "test_module")
    assert context.qualified_name == "test_module.foo"
    assert context.signature.startswith("def foo")
    assert context.docstring is None


def test_extract_function_with_comments(parser, get_root_node):
    code = b"""
# This is a test function
# It adds two numbers
def add(a, b):
    return a + b
"""
    root_node = get_root_node(code)
    context = parser.extract_function_context(root_node, code, "test_module")
    assert context.qualified_name == "test_module.add"
    assert context.docstring is None  # Docstring is None, comments are not captured


def test_extract_nested_function(parser, get_root_node):
    code = b"""
def outer():
    # inner does something
    def inner():
        pass
    return inner()
"""
    root_node = get_root_node(code)
    context = parser.extract_function_context(root_node, code, "test_module")
    names = [context.qualified_name]
    assert "test_module.outer" in names


def test_filter_nested_functions(parser, get_root_node):
    code = b"""
def outer():
    # inner does something
    def inner():
        pass
    return inner()
"""
    _parser = Parser(Language(tspython.language()))
    tree = _parser.parse(code)
    func_nodes = parser.filter_functions(tree, code, ["*"], [""])
    assert len(func_nodes) == 2
    assert func_nodes[0].type == "function_definition"
    assert func_nodes[1].type == "function_definition"
    assert (
        parser.get_node_text(func_nodes[0], code)
        == "def outer():\n    # inner does something\n    def inner():\n        pass\n    return inner()"
    )
    assert parser.get_node_text(func_nodes[1], code) == "def inner():\n        pass"


def test_extract_class_and_method(parser, get_root_node):
    code = b"""
class MyClass:
    # This is a method
    def method(self):
        pass
"""
    root_node = get_root_node(code)
    context = parser.extract_function_context(root_node, code, "test_module")
    assert "test_module.MyClass.method" in context.qualified_name
    assert context.docstring is None  # No docstring, only comments

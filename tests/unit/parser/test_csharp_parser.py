import pytest
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Parser, Language
from docmancer.parser.csharp_parser import CSharpParser
from docmancer.models.function_context import FunctionContextModel


@pytest.fixture
def parser():
    return CSharpParser()


@pytest.fixture
def get_root_node():
    def _get_root_node(source_code: str):
        _parser = Parser(Language(tscsharp.language()))
        tree = _parser.parse(source_code)
        return tree.root_node

    return _get_root_node


def test_extract_simple_method(parser, get_root_node):
    code = b"""
class Foo {
    public int Add(int x, int y) {
        return x + y;
    }
}
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "Foo")
    assert len(contexts) == 1
    ctx = contexts[0]
    assert "public int Add" in ctx.signature
    assert "return x + y;" in ctx.body
    assert ctx.return_type == "int"
    assert any(p.name == "x" for p in ctx.parameters)
    assert any(p.name == "y" for p in ctx.parameters)


def test_extract_method_with_comment(parser, get_root_node):
    code = b"""
class Bar {
    // This is a test method
    public void Test() {
    }
}
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "Bar")
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx.docstring is not None
    assert "This is a test method" in ctx.docstring.lines[0]


def test_get_enclosing_class_name(parser, get_root_node):
    code = b"""
class Baz {
    public void DoSomething() {
        return x + y;
    }
}
"""
    root_node = get_root_node(code)
    contexts = parser.extract_function_contexts(root_node, code, "Baz")
    assert len(contexts) == 1
    ctx = contexts[0]
    assert ctx.qualified_name == "Baz.Baz.DoSomething"
    assert ctx.signature.startswith("public void DoSomething")
    assert ctx.docstring is None

from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class BrokenTool(Tool):
    name = "broken"

    def call(self):
        raise TimeoutError("se acabó el tiempo")


class AddTool(Tool):
    name = "add"

    def call(self, a, b):
        return str(a + b)


def test_runs_tool_with_arguments():
    assert ToolRegistry([AddTool()]).run("add", {"a": 1, "b": 2}) == "3"


def test_unknown_tool_returns_error_text():
    assert "no existe" in ToolRegistry().run("nope", {})


def test_bad_arguments_return_error_text():
    assert "argumentos inválidos" in ToolRegistry([AddTool()]).run("add", {"a": 1})


def test_tool_failure_returns_error_text():
    assert "se acabó el tiempo" in ToolRegistry([BrokenTool()]).run("broken", None)

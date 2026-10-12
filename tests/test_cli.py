from app.cli import run
from app.errors import LlmUnavailable


class FakeAgent:
    def __init__(self, error=None):
        self.error = error
        self.resets = 0

    def reply(self, text):
        if self.error:
            raise self.error
        return f"eco {text}"

    def reset(self):
        self.resets += 1


def run_with(agent, *lines):
    inputs = iter(lines)
    output = []
    run(agent, read=lambda prompt: next(inputs), write=output.append)
    return output


def test_replies_and_exits():
    output = run_with(FakeAgent(), "hola", "/salir")
    assert output[1].startswith("BLOPA: eco hola")


def test_reset_command():
    agent = FakeAgent()
    run_with(agent, "/reset", "/salir")
    assert agent.resets == 1


def test_shows_clear_error_instead_of_crashing():
    output = run_with(FakeAgent(LlmUnavailable("http://ollama:11434")), "hola", "/salir")
    assert "No puedo conectar con Ollama" in output[1]

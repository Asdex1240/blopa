from app.agent import Agent
from app.system_prompt import SYSTEM_PROMPT
from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class FakeLlm:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append({"messages": list(messages), "tools": tools})
        answer = self.answers.pop(0)
        if isinstance(answer, dict):
            return {"role": "assistant", "content": "", **answer}
        return {"role": "assistant", "content": answer}


class EchoTool(Tool):
    name = "echo"
    description = "Repite el texto."

    def call(self, text):
        return f"eco: {text}"


def tool_call(name, **arguments):
    return {"tool_calls": [{"function": {"name": name, "arguments": arguments}}]}


def test_reply_sends_system_prompt_and_user_message():
    llm = FakeLlm("Hola")
    assert Agent(llm).reply("hola").text == "Hola"
    assert llm.calls[0]["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "hola"},
    ]


def test_remembers_previous_turns():
    llm = FakeLlm("Mucho gusto, Juan", "Te llamas Juan")
    agent = Agent(llm)
    agent.reply("me llamo Juan")
    agent.reply("¿cómo me llamo?")
    assert [m["content"] for m in llm.calls[1]["messages"][1:]] == [
        "me llamo Juan",
        "Mucho gusto, Juan",
        "¿cómo me llamo?",
    ]


def test_history_is_limited():
    agent = Agent(FakeLlm(*["ok"] * 15), history_limit=20)
    for number in range(15):
        agent.reply(f"mensaje {number}")
    assert len(agent.history) == 20
    assert agent.history[0]["content"] == "mensaje 5"


def test_reset_clears_history():
    agent = Agent(FakeLlm("ok"))
    agent.reply("hola")
    agent.reset()
    assert agent.history == []


def test_strips_think_blocks():
    agent = Agent(FakeLlm("<think>razonando</think>\n\nHola"))
    assert agent.reply("hola").text == "Hola"


def test_sends_tool_schemas_to_the_model():
    llm = FakeLlm("ok")
    Agent(llm, ToolRegistry([EchoTool()])).reply("hola")
    assert llm.calls[0]["tools"][0]["function"]["name"] == "echo"


def test_runs_requested_tool_and_returns_result_to_model():
    llm = FakeLlm(tool_call("echo", text="hola"), "Listo")
    reply = Agent(llm, ToolRegistry([EchoTool()])).reply("repite hola")
    assert reply.text == "Listo"
    assert reply.tools_used == ["echo"]
    assert llm.calls[1]["messages"][-1] == {"role": "tool", "tool_name": "echo", "content": "eco: hola"}


def test_history_keeps_only_user_and_final_answer():
    agent = Agent(FakeLlm(tool_call("echo", text="hola"), "Listo"), ToolRegistry([EchoTool()]))
    agent.reply("repite hola")
    assert [m["role"] for m in agent.history] == ["user", "assistant"]


def test_forces_final_answer_after_max_steps():
    llm = FakeLlm(*[tool_call("echo", text="otra vez")] * 5, "Me rendí")
    reply = Agent(llm, ToolRegistry([EchoTool()]), max_steps=5).reply("bucle")
    assert reply.text == "Me rendí"
    assert len(reply.tools_used) == 5
    assert llm.calls[-1]["tools"] is None


def test_adds_current_context_after_the_conversation():
    llm = FakeLlm("ok")
    Agent(llm, context=lambda: "Hoy es lunes 12 de octubre de 2026").reply("¿qué día es?")
    messages = llm.calls[0]["messages"]
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert messages[-1] == {"role": "system", "content": "Contexto actual: Hoy es lunes 12 de octubre de 2026"}


def test_system_prompt_stays_identical_between_turns():
    clock = iter(["Son las 10:00", "Son las 10:05"])
    llm = FakeLlm("uno", "dos")
    agent = Agent(llm, context=lambda: next(clock))
    agent.reply("hola")
    agent.reply("otra vez")
    first, second = llm.calls[0]["messages"], llm.calls[1]["messages"]
    assert second[: len(first) - 1] == first[:-1]


class HouseTool(EchoTool):
    name = "house"

    def required_for(self, text):
        return "luz" in text


def test_nudges_once_when_a_required_tool_was_skipped():
    llm = FakeLlm("Ya está apagada.", tool_call("house", text="sala"), "Apagada de verdad.")
    reply = Agent(llm, ToolRegistry([HouseTool()])).reply("apaga la luz")
    assert reply.text == "Apagada de verdad."
    assert reply.tools_used == ["house"]
    assert "llama a house" in llm.calls[1]["messages"][-1]["content"]


def test_nudge_happens_only_once():
    llm = FakeLlm("No sé.", "Sigo sin saber.")
    reply = Agent(llm, ToolRegistry([HouseTool()])).reply("apaga la luz")
    assert reply.text == "Sigo sin saber."
    assert len(llm.calls) == 2


def test_no_nudge_for_unrelated_messages():
    llm = FakeLlm("Hola")
    Agent(llm, ToolRegistry([HouseTool()])).reply("hola")
    assert len(llm.calls) == 1


def test_nudges_when_the_wrong_tool_was_used():
    class Lister(EchoTool):
        name = "lister"

    llm = FakeLlm(tool_call("lister", text="x"), "Solo listé.", tool_call("house", text="sala"), "Ahora sí.")
    reply = Agent(llm, ToolRegistry([HouseTool(), Lister()])).reply("apaga la luz")
    assert reply.text == "Ahora sí."
    assert reply.tools_used == ["lister", "house"]

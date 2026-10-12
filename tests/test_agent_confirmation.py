from app.agent import CANCELLED, Agent
from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class FakeLlm:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append(list(messages))
        answer = self.answers.pop(0)
        if isinstance(answer, dict):
            return {"role": "assistant", "content": "", **answer}
        return {"role": "assistant", "content": answer}


class SensitiveTool(Tool):
    name = "launch"

    def __init__(self):
        self.runs = []

    def confirmation_for(self, target):
        return f"Voy a lanzar {target}."

    def call(self, target):
        self.runs.append(target)
        return f"{target} lanzado"


def launch_call(target="cohete"):
    return {"tool_calls": [{"function": {"name": "launch", "arguments": {"target": target}}}]}


def agent_with(llm):
    tool = SensitiveTool()
    return Agent(llm, ToolRegistry([tool])), tool


def test_sensitive_tool_waits_for_confirmation():
    agent, tool = agent_with(FakeLlm(launch_call()))
    reply = agent.reply("lanza el cohete")
    assert reply.text == "Voy a lanzar cohete. ¿Lo hago?"
    assert reply.confirmation == "Voy a lanzar cohete."
    assert agent.pending_confirmation == "Voy a lanzar cohete."
    assert tool.runs == []


def test_yes_runs_the_tool_and_finishes():
    agent, tool = agent_with(FakeLlm(launch_call(), "Listo, cohete lanzado."))
    agent.reply("lanza el cohete")
    reply = agent.reply("sí, hazlo")
    assert tool.runs == ["cohete"]
    assert reply.text == "Listo, cohete lanzado."
    assert reply.tools_used == ["launch"]
    assert agent.pending_confirmation is None


def test_no_cancels_without_calling_the_model():
    llm = FakeLlm(launch_call())
    agent, tool = agent_with(llm)
    agent.reply("lanza el cohete")
    reply = agent.reply("mejor no")
    assert reply.text == CANCELLED
    assert tool.runs == []
    assert len(llm.calls) == 1


def test_other_message_cancels_and_is_answered_normally():
    agent, tool = agent_with(FakeLlm(launch_call(), "Son las 5."))
    agent.reply("lanza el cohete")
    reply = agent.reply("¿qué hora es?")
    assert reply.text == "Son las 5."
    assert tool.runs == []
    assert agent.pending_confirmation is None


def test_reset_clears_pending_action():
    agent, _ = agent_with(FakeLlm(launch_call()))
    agent.reply("lanza el cohete")
    agent.reset()
    assert agent.pending_confirmation is None


def test_history_hides_the_confirmation_exchange_after_yes():
    agent, _ = agent_with(FakeLlm(launch_call(), "Hecho."))
    agent.reply("lanza el cohete")
    agent.reply("dale")
    assert [m["content"] for m in agent.history] == ["lanza el cohete", "Hecho."]


def test_history_hides_the_confirmation_exchange_after_no():
    agent, _ = agent_with(FakeLlm(launch_call()))
    agent.reply("lanza el cohete")
    agent.reply("no")
    assert [m["content"] for m in agent.history] == ["lanza el cohete", CANCELLED]


def test_history_keeps_other_message_after_cancelling():
    agent, _ = agent_with(FakeLlm(launch_call(), "Son las 5."))
    agent.reply("lanza el cohete")
    agent.reply("¿qué hora es?")
    assert [m["content"] for m in agent.history] == ["lanza el cohete", "¿qué hora es?", "Son las 5."]


def test_drops_the_latest_confirmation_reply_only():
    agent, _ = agent_with(FakeLlm("¡Qué bien!", launch_call(), "Hecho."))
    agent.reply("sí")
    agent.reply("lanza el cohete")
    agent.reply("sí")
    assert [m["content"] for m in agent.history] == ["sí", "¡Qué bien!", "lanza el cohete", "Hecho."]

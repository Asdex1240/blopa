from app.agent import Agent
from app.system_prompt import SYSTEM_PROMPT


class FakeLlm:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append(messages)
        return {"role": "assistant", "content": self.answers.pop(0)}


def test_reply_sends_system_prompt_and_user_message():
    llm = FakeLlm("Hola")
    assert Agent(llm).reply("hola") == "Hola"
    assert llm.calls[0] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "hola"},
    ]


def test_remembers_previous_turns():
    llm = FakeLlm("Mucho gusto, Juan", "Te llamas Juan")
    agent = Agent(llm)
    agent.reply("me llamo Juan")
    agent.reply("¿cómo me llamo?")
    assert [m["content"] for m in llm.calls[1][1:]] == [
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
    assert agent.reply("hola") == "Hola"

import re
from dataclasses import dataclass, field

from app.concerns.conversation_memory import ConversationMemory
from app.system_prompt import SYSTEM_PROMPT
from app.tools.registry import ToolRegistry

THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)
MAX_STEPS = 5


@dataclass
class Reply:
    text: str
    tools_used: list = field(default_factory=list)


class Agent(ConversationMemory):
    def __init__(self, llm, registry=None, history_limit=20, max_steps=MAX_STEPS, context=lambda: ""):
        self.llm = llm
        self.registry = registry or ToolRegistry()
        self.context = context
        self.history_limit = history_limit
        self.max_steps = max_steps

    def reply(self, text):
        self.remember("user", text)
        messages = self._messages()
        tools_used = []
        for _ in range(self.max_steps):
            message = self.llm.chat(messages, tools=self.registry.schemas())
            calls = message.get("tool_calls") or []
            if not calls:
                return self._finish(message, tools_used)
            messages.append(message)
            for call in calls:
                name = call["function"]["name"]
                tools_used.append(name)
                result = self.registry.run(name, call["function"].get("arguments"))
                messages.append({"role": "tool", "tool_name": name, "content": result})
        return self._finish(self.llm.chat(messages), tools_used)

    def reset(self):
        self.forget()

    def _finish(self, message, tools_used):
        text = THINK_BLOCK.sub("", message.get("content", "")).strip()
        self.remember("assistant", text)
        return Reply(text, tools_used)

    def _messages(self):
        context = self.context()
        prompt = f"{SYSTEM_PROMPT}\nContexto actual: {context}" if context else SYSTEM_PROMPT
        return [{"role": "system", "content": prompt}, *self.history]

import re
from dataclasses import dataclass, field

from app.concerns.conversation_memory import ConversationMemory
from app.confirmation import PendingAction, classify
from app.system_prompt import SYSTEM_PROMPT
from app.tools.registry import ToolRegistry

THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)
MAX_STEPS = 5
CANCELLED = "Listo, no lo hice."


@dataclass
class Reply:
    text: str
    tools_used: list = field(default_factory=list)
    confirmation: str | None = None


class Agent(ConversationMemory):
    def __init__(self, llm, registry=None, history_limit=20, max_steps=MAX_STEPS, context=lambda: ""):
        self.llm = llm
        self.registry = registry or ToolRegistry()
        self.context = context
        self.history_limit = history_limit
        self.max_steps = max_steps
        self.pending = None

    @property
    def pending_confirmation(self):
        return self.pending and self.pending.description

    def reply(self, text):
        self.remember("user", text)
        if self.pending:
            return self._resolve(text)
        return self._run(self._messages(), [], self.max_steps)

    def reset(self):
        self.forget()
        self.pending = None

    def _run(self, messages, tools_used, steps):
        for step in range(steps):
            message = self.llm.chat(messages, tools=self.registry.schemas())
            calls = message.get("tool_calls") or []
            if not calls:
                return self._finish(message, tools_used)
            messages.append(message)
            for call in calls:
                name = call["function"]["name"]
                arguments = call["function"].get("arguments") or {}
                description = self.registry.confirmation_for(name, arguments)
                if description:
                    return self._ask(PendingAction(name, arguments, description, messages, tools_used, steps - step - 1))
                self._execute(name, arguments, messages, tools_used)
        return self._finish(self.llm.chat(messages), tools_used)

    def _execute(self, name, arguments, messages, tools_used):
        tools_used.append(name)
        result = self.registry.run(name, arguments)
        messages.append({"role": "tool", "tool_name": name, "content": result})

    def _ask(self, action):
        self.pending = action
        text = f"{action.description} ¿Lo hago?"
        self.remember("assistant", text)
        return Reply(text, list(action.tools_used), confirmation=action.description)

    def _resolve(self, text):
        action, self.pending = self.pending, None
        answer = classify(text)
        self.drop({"role": "assistant", "content": f"{action.description} ¿Lo hago?"})
        if answer != "other":
            self.drop({"role": "user", "content": text})
        if answer == "yes":
            self._execute(action.name, action.arguments, action.messages, action.tools_used)
            return self._run(action.messages, action.tools_used, max(action.steps_left, 1))
        if answer == "no":
            self.remember("assistant", CANCELLED)
            return Reply(CANCELLED)
        return self._run(self._messages(), [], self.max_steps)

    def _finish(self, message, tools_used):
        text = THINK_BLOCK.sub("", message.get("content", "")).strip()
        self.remember("assistant", text)
        return Reply(text, tools_used)

    def _messages(self):
        context = self.context()
        prompt = f"{SYSTEM_PROMPT}\nContexto actual: {context}" if context else SYSTEM_PROMPT
        return [{"role": "system", "content": prompt}, *self.history]

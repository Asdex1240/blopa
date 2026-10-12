import re

from app.concerns.conversation_memory import ConversationMemory
from app.system_prompt import SYSTEM_PROMPT

THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


class Agent(ConversationMemory):
    def __init__(self, llm, history_limit=20):
        self.llm = llm
        self.history_limit = history_limit

    def reply(self, text):
        self.remember("user", text)
        message = self.llm.chat(self._messages())
        answer = THINK_BLOCK.sub("", message.get("content", "")).strip()
        self.remember("assistant", answer)
        return answer

    def reset(self):
        self.forget()

    def _messages(self):
        return [{"role": "system", "content": SYSTEM_PROMPT}, *self.history]

class ConversationMemory:
    history_limit = 20

    @property
    def history(self):
        if not hasattr(self, "_history"):
            self._history = []
        return self._history

    def remember(self, role, content):
        self.history.append({"role": role, "content": content})
        del self.history[: max(0, len(self.history) - self.history_limit)]

    def forget(self):
        self.history.clear()

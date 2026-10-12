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

    def drop(self, message):
        for index in range(len(self.history) - 1, -1, -1):
            if self.history[index] == message:
                del self.history[index]
                return

    def forget(self):
        self.history.clear()

class TruncatesText:
    max_chars = 3000

    def truncate(self, text):
        if len(text) <= self.max_chars:
            return text
        return text[: self.max_chars].rsplit(" ", 1)[0] + " […]"

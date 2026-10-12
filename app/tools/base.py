class Tool:
    name = ""
    description = ""
    parameters = {"type": "object", "properties": {}, "required": []}

    def call(self, **arguments):
        raise NotImplementedError

    def available(self):
        return True

    def confirmation_for(self, **arguments):
        return None

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

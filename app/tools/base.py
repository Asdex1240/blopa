class Tool:
    name = ""
    description = ""
    parameters = {"type": "object", "properties": {}, "required": []}

    def call(self, **arguments):
        raise NotImplementedError

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

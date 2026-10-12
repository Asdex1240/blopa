class ToolRegistry:
    def __init__(self, tools=()):
        self.tools = {tool.name: tool for tool in tools}

    def schemas(self):
        return [tool.schema() for tool in self.tools.values()]

    def run(self, name, arguments):
        tool = self.tools.get(name)
        if tool is None:
            return f"Error: la herramienta {name} no existe."
        try:
            return tool.call(**(arguments or {}))
        except TypeError as error:
            return f"Error: argumentos inválidos para {name}: {error}"
        except Exception as error:
            return f"Error: {name} falló: {error}"

from app.tools.base import Tool


class RunAutomationTool(Tool):
    name = "run_automation"

    def __init__(self, repository, runner):
        self.repository = repository
        self.runner = runner

    def available(self):
        return bool(self.repository.list())

    def schema(self):
        automations = self.repository.list()
        catalog = "; ".join(f"«{item.name}»: {item.description}" for item in automations)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (
                    "Ejecuta una automatización de n8n que el usuario registró. "
                    f"Úsala cuando el usuario pida lanzar, correr o ejecutar alguna de estas: {catalog}."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "enum": [item.name for item in automations],
                            "description": "Nombre exacto de la automatización.",
                        },
                        "input": {
                            "type": "string",
                            "description": "Texto opcional que el usuario quiere enviar al flujo.",
                        },
                    },
                    "required": ["name"],
                },
            },
        }

    def confirmation_for(self, name, input=""):
        automation = self.repository.find_by_name(name)
        if automation is None or not automation.requires_confirmation:
            return None
        return f"Voy a ejecutar la automatización «{automation.name}»: {automation.description}"

    def call(self, name, input=""):
        automation = self.repository.find_by_name(name)
        if automation is None:
            available = ", ".join(f"«{item.name}»" for item in self.repository.list()) or "ninguna"
            return f"No existe una automatización llamada «{name}». Las disponibles son: {available}."
        run = self.runner.run(automation, input or "", source="chat")
        if run.ok:
            return f"La automatización «{automation.name}» se ejecutó correctamente. Respuesta de n8n: {run.detail or '(vacía)'}"
        return f"La automatización «{automation.name}» falló: {run.detail or f'código {run.status_code}'}"

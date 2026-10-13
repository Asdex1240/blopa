from app.concerns.mentions_home import MentionsHome
from app.home.catalog import ACTION_NAMES, is_sensitive
from app.home.devices import DeviceNotFound, InvalidAction
from app.tools.base import Tool

ACTION_DESCRIPTIONS = {
    "encender": "encender",
    "apagar": "apagar",
    "ajustar_brillo": "ajustar el brillo al {value}% de",
    "bloquear": "cerrar con llave",
    "desbloquear": "quitar la llave de",
    "abrir": "abrir",
    "cerrar": "cerrar",
    "detener": "detener",
    "ajustar_temperatura": "poner a {value} °C",
    "ejecutar": "ejecutar",
}


class HomeListDevicesTool(MentionsHome, Tool):
    name = "home_list_devices"
    description = (
        "Lista todos los dispositivos de la casa con su estado. Úsala solo para preguntas generales como "
        "«¿qué luces hay?» o «¿qué está prendido?». Nunca la uses para encender, apagar o ajustar algo: para eso usa home_control_device."
    )

    def __init__(self, directory):
        self.directory = directory

    def required_for(self, text):
        return self.is_question(text)

    def call(self):
        devices = self.directory.list()
        if not devices:
            return "No hay dispositivos en Home Assistant."
        return "\n".join(f"- {device.name} ({device.kind}): {device.state_label}" for device in devices)


class HomeDeviceStatusTool(MentionsHome, Tool):
    name = "home_device_status"
    description = "Consulta el estado de un dispositivo de la casa por su nombre, por ejemplo «luz de la sala»."
    parameters = {
        "type": "object",
        "properties": {"device": {"type": "string", "description": "Nombre del dispositivo como lo dice el usuario."}},
        "required": ["device"],
    }

    def __init__(self, directory):
        self.directory = directory

    def required_for(self, text):
        return self.is_question(text)

    def call(self, device):
        try:
            found = self.directory.find(device)
        except DeviceNotFound as error:
            return str(error)
        return f"{found.name} ({found.kind}) está {found.state_label}."


class HomeControlDeviceTool(MentionsHome, Tool):
    name = "home_control_device"
    description = (
        "Ejecuta una orden en un dispositivo de la casa: encender o apagar luces y enchufes, ajustar brillo (0-100), "
        "bloquear o desbloquear cerraduras, abrir o cerrar persianas, ajustar temperatura del clima. "
        "Úsala directo, sin listar antes; si el usuario dice «ponlo», «apágalo» o «súbele», usa el dispositivo del que venían hablando."
    )
    parameters = {
        "type": "object",
        "properties": {
            "device": {"type": "string", "description": "Nombre del dispositivo como lo dice el usuario."},
            "action": {"type": "string", "enum": ACTION_NAMES, "description": "Acción a realizar."},
            "value": {"type": "number", "description": "Solo para ajustar_brillo (1-100) o ajustar_temperatura (°C)."},
        },
        "required": ["device", "action"],
    }

    def __init__(self, directory):
        self.directory = directory

    def required_for(self, text):
        return self.is_command(text)

    def confirmation_for(self, device, action, value=None):
        try:
            found = self.directory.find(device)
        except DeviceNotFound:
            return None
        if not is_sensitive(found.domain):
            return None
        verb = ACTION_DESCRIPTIONS.get(action, action).format(value=value)
        return f"Voy a {verb} «{found.name}» ({found.kind})."

    def call(self, device, action, value=None):
        try:
            found = self.directory.find(device)
            self.directory.control(found, action, value)
            updated = self.directory.settled(found.entity_id, before=found)
        except (DeviceNotFound, InvalidAction) as error:
            return str(error)
        if updated.state == found.state and updated.attributes == found.attributes:
            return f"Mandé la orden, pero «{found.name}» sigue {updated.state_label}. Puede que ya estuviera así o que no respondiera."
        return f"Hecho. «{found.name}» ahora está {updated.state_label}."

import difflib
import time
from dataclasses import asdict, dataclass

from app.confirmation import normalize
from app.home.client import HomeAssistantError
from app.home.catalog import ACTIONS, DOMAIN_LABELS, STATE_LABELS, VALUE_RANGES, actions_for, is_sensitive

TRANSITIONAL_STATES = {"locking", "unlocking", "opening", "closing"}
KIND_WORDS = {
    "light": {"luz", "luces", "foco", "focos", "lampara", "lamparas"},
    "switch": {"enchufe", "enchufes", "contacto", "contactos"},
    "fan": {"ventilador", "ventiladores"},
    "lock": {"cerradura", "cerraduras", "chapa"},
    "cover": {"persiana", "persianas", "cortina", "cortinas", "cochera"},
    "climate": {"aire", "clima", "termostato"},
}
KEY_ATTRIBUTES = ("brightness", "current_temperature", "temperature", "current_position", "hvac_modes")
FILLER_WORDS = {"el", "la", "los", "las", "de", "del", "mi", "un", "una"}


class DeviceNotFound(Exception):
    pass


class InvalidAction(Exception):
    pass


@dataclass(frozen=True)
class Device:
    entity_id: str
    name: str
    domain: str
    state: str
    attributes: dict

    @property
    def kind(self):
        return DOMAIN_LABELS[self.domain]

    @property
    def state_label(self):
        label = STATE_LABELS.get(self.state, self.state)
        brightness = self.attributes.get("brightness")
        if self.domain == "light" and self.state == "on" and brightness:
            return f"{label} al {round(brightness / 255 * 100)}%"
        if self.domain == "climate" and self.attributes.get("current_temperature") is not None:
            target = self.attributes.get("temperature")
            suffix = f" (objetivo {target} °C)" if target is not None else ""
            return f"{label}, {self.attributes['current_temperature']} °C{suffix}"
        if self.domain == "cover" and self.attributes.get("current_position") is not None:
            return f"{label} al {self.attributes['current_position']}%"
        return label

    def to_dict(self):
        return {
            **asdict(self),
            "kind": self.kind,
            "state_label": self.state_label,
            "sensitive": is_sensitive(self.domain),
            "actions": actions_for(self.domain),
        }


def from_state(state):
    domain = state["entity_id"].split(".", 1)[0]
    attributes = state.get("attributes", {})
    return Device(
        entity_id=state["entity_id"],
        name=attributes.get("friendly_name") or state["entity_id"],
        domain=domain,
        state=state.get("state", "unknown"),
        attributes={key: attributes[key] for key in KEY_ATTRIBUTES if key in attributes},
    )


def comparable(text):
    return " ".join(word for word in normalize(text).split() if word not in FILLER_WORDS)


class DeviceDirectory:
    def __init__(self, client, socket=None, settle_seconds=5.0, poll_seconds=0.5, sleep=time.sleep):
        self.client = client
        self.socket = socket
        self.settle_seconds = settle_seconds
        self.poll_seconds = poll_seconds
        self.sleep = sleep

    def list(self):
        devices = [from_state(state) for state in self.client.states() if state["entity_id"].split(".", 1)[0] in ACTIONS]
        return sorted(devices, key=lambda device: (device.domain, device.name.lower()))

    def get(self, entity_id):
        for device in self.list():
            if device.entity_id == entity_id:
                return device
        raise DeviceNotFound(f"No existe el dispositivo {entity_id}.")

    def settled(self, entity_id, before=None):
        device = self.get(entity_id)
        waited = 0.0
        while self._pending(device, before) and waited < self.settle_seconds:
            self.sleep(self.poll_seconds)
            waited += self.poll_seconds
            device = self.get(entity_id)
        return device

    def _pending(self, device, before):
        unchanged = before is not None and (device.state, device.attributes) == (before.state, before.attributes)
        return device.state in TRANSITIONAL_STATES or unchanged

    def find(self, query):
        devices = self.list()
        wanted = comparable(query)
        for device in devices:
            if device.entity_id == query.strip() or comparable(device.name) == wanted:
                return device
        containing = [device for device in devices if wanted and (wanted in comparable(device.name) or comparable(device.name) in wanted)]
        if len(containing) == 1:
            return containing[0]
        names = {comparable(device.name): device for device in (containing or devices)}
        close = difflib.get_close_matches(wanted, names, n=3, cutoff=0.6)
        if len(close) == 1 or (close and len(containing) > 1):
            return names[close[0]]
        only = self._only_device_of_spoken_kind(query, devices)
        if only:
            return only
        candidates = ", ".join(f"«{device.name}»" for device in (containing or devices)[:8])
        raise DeviceNotFound(f"No encontré un dispositivo llamado «{query}». Opciones: {candidates}.")

    def rename(self, entity_id, name):
        self.get(entity_id)
        try:
            self.socket.call("config/entity_registry/update", entity_id=entity_id, name=name.strip())
        except HomeAssistantError as error:
            if "not found" in str(error).lower():
                raise InvalidAction("Este dispositivo no permite cambiarle el nombre desde BLOPA.")
            raise
        return self.get(entity_id)

    def _only_device_of_spoken_kind(self, query, devices):
        words = set(normalize(query).split())
        domains = [domain for domain, kind_words in KIND_WORDS.items() if words & kind_words]
        if len(domains) != 1:
            return None
        matching = [device for device in devices if device.domain == domains[0]]
        return matching[0] if len(matching) == 1 else None

    def control(self, device, action, value=None):
        definition = ACTIONS[device.domain].get(action)
        if definition is None:
            allowed = ", ".join(actions_for(device.domain))
            raise InvalidAction(f"«{device.name}» ({device.kind}) no acepta «{action}». Acciones permitidas: {allowed}.")
        data = {"entity_id": device.entity_id}
        if definition.needs_value:
            data[definition.needs_value] = self._checked_value(definition.needs_value, value)
        self.client.call_service(device.domain, definition.service, data)
        return data

    def _checked_value(self, field, value):
        low, high = VALUE_RANGES[field]
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise InvalidAction(f"Necesito un número entre {low} y {high}.")
        if not low <= number <= high:
            raise InvalidAction(f"El valor debe estar entre {low} y {high}.")
        return round(number) if field == "brightness_pct" else number

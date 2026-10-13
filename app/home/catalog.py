from dataclasses import dataclass

DOMAIN_LABELS = {
    "light": "luz",
    "switch": "enchufe",
    "fan": "ventilador",
    "lock": "cerradura",
    "cover": "persiana",
    "climate": "clima",
    "script": "script",
    "automation": "automatización",
}

SENSITIVE_DOMAINS = {"lock", "cover", "climate", "script", "automation"}

STATE_LABELS = {
    "on": "encendido",
    "off": "apagado",
    "locked": "cerrada con llave",
    "unlocked": "abierta (sin llave)",
    "locking": "cerrando con llave",
    "unlocking": "quitando llave",
    "jammed": "atorada: no pudo cerrar con llave, hay que revisarla",
    "open": "abierta",
    "closed": "cerrada",
    "opening": "abriéndose",
    "closing": "cerrándose",
    "heat": "calefacción",
    "cool": "enfriando",
    "heat_cool": "automático",
    "auto": "automático",
    "dry": "deshumidificando",
    "fan_only": "solo ventilador",
    "unavailable": "no disponible",
    "unknown": "desconocido",
}


@dataclass(frozen=True)
class Action:
    service: str
    needs_value: str | None = None


ACTIONS = {
    "light": {
        "encender": Action("turn_on"),
        "apagar": Action("turn_off"),
        "ajustar_brillo": Action("turn_on", needs_value="brightness_pct"),
    },
    "switch": {"encender": Action("turn_on"), "apagar": Action("turn_off")},
    "fan": {"encender": Action("turn_on"), "apagar": Action("turn_off")},
    "lock": {"bloquear": Action("lock"), "desbloquear": Action("unlock")},
    "cover": {"abrir": Action("open_cover"), "cerrar": Action("close_cover"), "detener": Action("stop_cover")},
    "climate": {
        "encender": Action("turn_on"),
        "apagar": Action("turn_off"),
        "ajustar_temperatura": Action("set_temperature", needs_value="temperature"),
    },
    "script": {"ejecutar": Action("turn_on")},
    "automation": {"ejecutar": Action("trigger")},
}

ACTION_NAMES = sorted({name for actions in ACTIONS.values() for name in actions})

VALUE_RANGES = {"brightness_pct": (1, 100), "temperature": (10, 35)}


def actions_for(domain):
    return list(ACTIONS.get(domain, {}))


def is_sensitive(domain):
    return domain in SENSITIVE_DOMAINS

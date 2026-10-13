from app.confirmation import normalize
from app.home.devices import comparable

HOME_NOUNS = {
    "luz", "luces", "foco", "focos", "lampara", "lamparas", "enchufe", "contacto", "ventilador",
    "cerradura", "puerta", "puertas", "persiana", "persianas", "cortina", "cochera", "termostato",
}
PRONOUN_COMMANDS = {
    "ponlo", "ponla", "prendelo", "prendela", "enciendelo", "enciendela", "apagalo", "apagala",
    "subele", "subelo", "subela", "bajale", "bajalo", "bajala", "abrelo", "abrela", "cierralo", "cierrala", "atenualo",
}
COMMAND_WORDS = PRONOUN_COMMANDS | {
    "pon", "prende", "enciende", "apaga", "sube", "baja", "abre", "cierra", "bloquea", "desbloquea", "ajusta", "atenua",
}
STATE_WORDS = {
    "prendido", "prendida", "prendidos", "prendidas", "encendido", "encendida", "encendidos", "encendidas",
    "apagado", "apagada", "apagados", "apagadas", "abierta", "abierto", "cerrada", "cerrado",
}
QUESTION_WORDS = STATE_WORDS | {"esta", "estan", "hay", "estado", "cuales", "que"}


class MentionsHome:
    def mentions_device(self, text):
        if set(normalize(text).split()) & HOME_NOUNS:
            return True
        spoken = comparable(text)
        try:
            return any(comparable(device.name) in spoken for device in self.directory.list())
        except Exception:
            return False

    def is_command(self, text):
        words = set(normalize(text).split())
        return bool(words & PRONOUN_COMMANDS) or (bool(words & COMMAND_WORDS) and self.mentions_device(text))

    def is_question(self, text):
        words = set(normalize(text).split())
        if self.is_command(text) or not words & QUESTION_WORDS:
            return False
        return bool(words & STATE_WORDS) or self.mentions_device(text)

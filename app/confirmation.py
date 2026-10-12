import re
import unicodedata
from dataclasses import dataclass, field

YES_PHRASES = {"si", "dale", "confirmo", "hazlo", "si hazlo", "adelante", "ok", "va", "claro", "si por favor", "si dale", "confirmado"}
NO_PHRASES = {"no", "cancela", "mejor no", "no gracias", "cancelar", "no lo hagas", "detente", "alto"}


@dataclass
class PendingAction:
    name: str
    arguments: dict
    description: str
    messages: list = field(default_factory=list)
    tools_used: list = field(default_factory=list)
    steps_left: int = 1


def normalize(text):
    without_accents = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", without_accents)).strip()


def classify(text):
    phrase = normalize(text)
    if phrase in YES_PHRASES:
        return "yes"
    if phrase in NO_PHRASES:
        return "no"
    return "other"

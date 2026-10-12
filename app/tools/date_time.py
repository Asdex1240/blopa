from datetime import datetime
from zoneinfo import ZoneInfo

from app.tools.base import Tool

DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


class DateTimeTool(Tool):
    name = "date_time"
    description = "Devuelve la fecha, la hora y la zona horaria actuales del usuario."

    def __init__(self, timezone, clock=datetime.now):
        self.timezone = ZoneInfo(timezone)
        self.clock = clock

    def call(self):
        now = self.clock(self.timezone)
        return (
            f"Hoy es {DAYS[now.weekday()]} {now.day} de {MONTHS[now.month - 1]} de {now.year}, "
            f"son las {now:%H:%M} ({self.timezone.key}). Fecha ISO: {now:%Y-%m-%d}."
        )

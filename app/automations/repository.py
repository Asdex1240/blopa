import sqlite3

from app.automations.models import Automation, AutomationRun
from app.errors import BlopaError

EDITABLE_COLUMNS = {"name", "description", "webhook_path", "requires_confirmation"}

RUN_COLUMNS = """
    runs.id, runs.automation_id, automations.name AS automation_name, runs.started_at,
    runs.ok, runs.status_code, runs.detail, runs.duration_ms, runs.source
"""


class DuplicateAutomation(BlopaError):
    def __init__(self, name):
        super().__init__(f"Ya existe una automatización llamada «{name}».")


class AutomationRepository:
    def __init__(self, database):
        self.database = database

    def list(self):
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM automations ORDER BY name COLLATE NOCASE").fetchall()
        return [self._automation(row) for row in rows]

    def get(self, automation_id):
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM automations WHERE id = ?", (automation_id,)).fetchone()
        return row and self._automation(row)

    def find_by_name(self, name):
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM automations WHERE name = ? COLLATE NOCASE", (name.strip(),)).fetchone()
        return row and self._automation(row)

    def create(self, name, description, webhook_path, requires_confirmation=True):
        try:
            with self.database.connect() as connection:
                cursor = connection.execute(
                    "INSERT INTO automations (name, description, webhook_path, requires_confirmation) VALUES (?, ?, ?, ?)",
                    (name, description, webhook_path, int(requires_confirmation)),
                )
        except sqlite3.IntegrityError:
            raise DuplicateAutomation(name)
        return self.get(cursor.lastrowid)

    def update(self, automation_id, **fields):
        fields = {column: value for column, value in fields.items() if column in EDITABLE_COLUMNS}
        if not fields:
            return self.get(automation_id)
        if "requires_confirmation" in fields:
            fields["requires_confirmation"] = int(fields["requires_confirmation"])
        assignments = ", ".join(f"{column} = ?" for column in fields)
        try:
            with self.database.connect() as connection:
                connection.execute(
                    f"UPDATE automations SET {assignments}, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
                    (*fields.values(), automation_id),
                )
        except sqlite3.IntegrityError:
            raise DuplicateAutomation(fields.get("name", ""))
        return self.get(automation_id)

    def delete(self, automation_id):
        with self.database.connect() as connection:
            return connection.execute("DELETE FROM automations WHERE id = ?", (automation_id,)).rowcount > 0

    def record_run(self, automation_id, ok, status_code, detail, duration_ms, source):
        with self.database.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO automation_runs (automation_id, ok, status_code, detail, duration_ms, source) VALUES (?, ?, ?, ?, ?, ?)",
                (automation_id, int(ok), status_code, detail, duration_ms, source),
            )
            row = connection.execute(
                f"SELECT {RUN_COLUMNS} FROM automation_runs AS runs JOIN automations ON automations.id = runs.automation_id WHERE runs.id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return self._run(row)

    def runs(self, automation_id=None, limit=50):
        query = f"SELECT {RUN_COLUMNS} FROM automation_runs AS runs JOIN automations ON automations.id = runs.automation_id"
        parameters = ()
        if automation_id is not None:
            query += " WHERE runs.automation_id = ?"
            parameters = (automation_id,)
        with self.database.connect() as connection:
            rows = connection.execute(f"{query} ORDER BY runs.id DESC LIMIT ?", (*parameters, limit)).fetchall()
        return [self._run(row) for row in rows]

    def last_runs(self):
        with self.database.connect() as connection:
            rows = connection.execute(
                f"SELECT {RUN_COLUMNS} FROM automation_runs AS runs JOIN automations ON automations.id = runs.automation_id "
                "WHERE runs.id IN (SELECT MAX(id) FROM automation_runs GROUP BY automation_id)"
            ).fetchall()
        return {row["automation_id"]: self._run(row) for row in rows}

    def _automation(self, row):
        return Automation(**{**dict(row), "requires_confirmation": bool(row["requires_confirmation"])})

    def _run(self, row):
        return AutomationRun(**{**dict(row), "ok": bool(row["ok"])})

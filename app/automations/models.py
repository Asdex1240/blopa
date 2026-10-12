from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Automation:
    id: int
    name: str
    description: str
    webhook_path: str
    requires_confirmation: bool
    created_at: str
    updated_at: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class AutomationRun:
    id: int
    automation_id: int
    automation_name: str
    started_at: str
    ok: bool
    status_code: int | None
    detail: str
    duration_ms: int
    source: str

    def to_dict(self):
        return asdict(self)

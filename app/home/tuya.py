from app.errors import BlopaError

QR_PREFIX = "tuyaSmart--qrLogin?token="


class TuyaLinkError(BlopaError):
    pass


def qr_from(step):
    for field in step.get("data_schema") or []:
        data = (field.get("selector") or {}).get("qr_code", {}).get("data")
        if data:
            return data
    return None


class TuyaAccounts:
    def __init__(self, client):
        self.client = client

    def list(self):
        return [{"id": entry["entry_id"], "provider": "tuya", "title": entry["title"], "state": entry.get("state")} for entry in self.client.config_entries("tuya")]

    def start(self, user_code):
        flow = self.client.start_flow("tuya")
        step = self.client.continue_flow(flow["flow_id"], {"user_code": user_code.strip()})
        if step.get("step_id") != "scan":
            self.client.abort_flow(flow["flow_id"])
            detail = (step.get("description_placeholders") or {}).get("msg")
            raise TuyaLinkError(
                "Smart Life no reconoció ese código de usuario. Cópialo de nuevo desde "
                "Yo → Configuración → Cuenta y seguridad → Código de usuario." + (f" ({detail})" if detail else "")
            )
        return {"id": flow["flow_id"], "qr": qr_from(step)}

    def confirm(self, link_id):
        step = self.client.continue_flow(link_id, {})
        if step.get("type") == "create_entry":
            return {"connected": True, "title": step.get("title"), "qr": None}
        if step.get("type") == "abort":
            raise TuyaLinkError("La conexión se canceló. Empieza de nuevo con tu código de usuario.")
        return {"connected": False, "title": None, "qr": qr_from(step)}

    def cancel(self, link_id):
        self.client.abort_flow(link_id)

    def refresh(self):
        for entry in self.client.config_entries("tuya"):
            self.client.reload_entry(entry["entry_id"])

import { HouseIcon, MessageCircleIcon, SettingsIcon, WorkflowIcon } from "lucide-react"

import type { ServiceState, View } from "@/presentation/types/layout/types"

export const VIEWS: View[] = [
  { id: "chat", label: "Chat", icon: MessageCircleIcon },
  { id: "devices", label: "Dispositivos", icon: HouseIcon },
  { id: "automations", label: "Automatizaciones", icon: WorkflowIcon },
  { id: "settings", label: "Ajustes", icon: SettingsIcon },
]

export const HEALTH_REFRESH_MS = 15000

export const SERVICE_DOT: Record<ServiceState, string> = {
  ok: "bg-success",
  warn: "bg-warning",
  error: "bg-destructive",
  off: "bg-muted-foreground/40",
}

export const SERVICE_LABELS = ["Modelo", "Ollama", "n8n", "Home Assistant"]

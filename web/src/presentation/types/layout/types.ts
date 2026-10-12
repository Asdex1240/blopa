import type { LucideIcon } from "lucide-react"

export type ViewId = "chat" | "devices" | "automations" | "settings"

export type View = { id: ViewId; label: string; icon: LucideIcon }

export type ServiceState = "ok" | "warn" | "error" | "off"

export type Service = { label: string; state: ServiceState; detail: string }

export type Theme = "light" | "dark"

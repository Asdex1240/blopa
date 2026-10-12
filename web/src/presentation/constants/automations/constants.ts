import type { AutomationInput } from "@/presentation/types/automations/types"

export const EMPTY_AUTOMATION: AutomationInput = {
  name: "",
  description: "",
  webhook_path: "",
  requires_confirmation: true,
}

export const WEBHOOK_PATH_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*(\/[A-Za-z0-9_-]+)*$/

export const WEBHOOK_PREFIX = "n8n /webhook/"

export const RUN_HISTORY_LIMIT = 20

export const SOURCE_LABELS = { chat: "Chat", panel: "Panel" }

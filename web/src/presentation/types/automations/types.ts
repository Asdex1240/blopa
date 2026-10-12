export type AutomationRun = {
  id: number
  automation_id: number
  automation_name: string
  started_at: string
  ok: boolean
  status_code: number | null
  detail: string
  duration_ms: number
  source: "chat" | "panel"
}

export type Automation = {
  id: number
  name: string
  description: string
  webhook_path: string
  webhook_url: string
  requires_confirmation: boolean
  created_at: string
  updated_at: string
  last_run: AutomationRun | null
}

export type AutomationInput = {
  name: string
  description: string
  webhook_path: string
  requires_confirmation: boolean
}

export type AutomationFormErrors = Partial<Record<keyof AutomationInput, string>>

export type ChatRole = "user" | "assistant"

export type HistoryMessage = { role: ChatRole; content: string }

export type Reply = { text: string; tools_used: string[]; confirmation: string | null; elapsed: number }

export type History = { messages: HistoryMessage[]; confirmation: string | null }

export type OllamaStatus = { reachable: boolean; model_available: boolean; model_loaded: boolean }

export type Health = {
  status: string
  model: string
  timezone: string
  auth_required: boolean
  tools: string[]
  services: {
    ollama: OllamaStatus
    n8n: { configured: boolean; reachable: boolean }
    home_assistant: { configured: boolean; reachable: boolean }
    matter: { configured: boolean; reachable: boolean }
  }
}

import type { ChatRole } from "@/presentation/types/api/types"

export type ChatMessage = {
  id: number
  role: ChatRole | "error"
  text: string
  tools?: string[]
  elapsed?: number
}

export type MicrophoneState = "unknown" | "ready" | "denied"

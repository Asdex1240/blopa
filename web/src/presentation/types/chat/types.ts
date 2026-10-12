import type { ChatRole } from "@/presentation/types/api/types"

export type ChatMessage = {
  id: number
  role: ChatRole | "error"
  text: string
  tools?: string[]
  elapsed?: number
  confirmation?: string | null
}

export type MicrophoneState = "unknown" | "ready" | "denied"

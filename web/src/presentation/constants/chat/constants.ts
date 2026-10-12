import type { MicrophoneState } from "@/presentation/types/chat/types"

export const GREETING = "Hola, ¿en qué te ayudo?"

export const TYPING_DELAYS_MS = [0, 150, 300]

export const MIC_COLOR: Record<MicrophoneState, string> = {
  unknown: "",
  ready: "text-success",
  denied: "text-destructive",
}

export const CONFIRM_TEXT = "Sí, hazlo"

export const CANCEL_TEXT = "No"

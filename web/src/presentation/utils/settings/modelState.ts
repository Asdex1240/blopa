import type { Health } from "@/presentation/types/api/types"

export function modelState(health: Health) {
  const ollama = health.services.ollama
  if (!ollama.model_available) return "No descargado"
  return ollama.model_loaded ? "Cargado en memoria" : "Descargado, se cargará al usarlo"
}

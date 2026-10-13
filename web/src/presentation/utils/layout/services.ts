import { SERVICE_LABELS } from "@/presentation/constants/layout/constants"
import type { Health } from "@/presentation/types/api/types"
import type { Service } from "@/presentation/types/layout/types"

function modelService(health: Health): Service {
  const ollama = health.services.ollama
  if (!ollama.reachable || !ollama.model_available) {
    return { label: "Modelo", state: "error", detail: `${health.model} no está disponible` }
  }
  if (ollama.model_loaded) return { label: "Modelo", state: "ok", detail: `${health.model} cargado en memoria` }
  return { label: "Modelo", state: "warn", detail: `${health.model} se cargará al usarlo` }
}

function n8nService(n8n: Health["services"]["n8n"]): Service {
  if (!n8n.configured) return { label: "n8n", state: "off", detail: "No configurado" }
  return n8n.reachable
    ? { label: "n8n", state: "ok", detail: "Conectado" }
    : { label: "n8n", state: "error", detail: "Configurado, pero no responde" }
}

function homeAssistantService(home: Health["services"]["home_assistant"]): Service {
  if (!home.configured) return { label: "Home Assistant", state: "off", detail: "No configurado" }
  return home.reachable
    ? { label: "Home Assistant", state: "ok", detail: "Conectado" }
    : { label: "Home Assistant", state: "error", detail: "Configurado, pero no responde" }
}

function voiceService(voice: Health["services"]["voice"]): Service {
  if (!voice?.configured) return { label: "Voz", state: "off", detail: "No configurado" }
  if (!voice.reachable) return { label: "Voz", state: "error", detail: "Configurado, pero no responde" }
  return voice.ready
    ? { label: "Voz", state: "ok", detail: `Reconocimiento listo (${voice.model})` }
    : { label: "Voz", state: "warn", detail: `Cargando modelo ${voice.model}` }
}

export function buildServices(health: Health | null, online: boolean): Service[] {
  if (!online || !health) {
    return SERVICE_LABELS.map((label) => ({ label, state: "error", detail: "Sin conexión con el servidor" }))
  }
  const { ollama, n8n, home_assistant } = health.services
  return [
    modelService(health),
    { label: "Ollama", state: ollama.reachable ? "ok" : "error", detail: ollama.reachable ? "Conectado" : "Sin conexión" },
    n8nService(n8n),
    homeAssistantService(home_assistant),
    voiceService(health.services.voice),
  ]
}

import { storage } from "@/lib/storage"
import type { Health, HistoryMessage, Reply } from "@/presentation/types/api/types"

export const TOKEN_KEY = "blopa_token"

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

const describe = (detail: unknown) => {
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) return "El mensaje no es válido."
  return "Algo salió mal."
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  const token = storage.get(TOKEN_KEY)
  if (token) headers.Authorization = `Bearer ${token}`
  let response: Response
  try {
    response = await fetch(path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin",
    })
  } catch {
    throw new ApiError(0, "No puedo conectar con el servidor de BLOPA.")
  }
  if (response.status === 204) return undefined as T
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new ApiError(response.status, describe(data.detail))
  return data as T
}

export const api = {
  health: () => request<Health>("GET", "/health"),
  listMessages: () => request<{ messages: HistoryMessage[] }>("GET", "/chat/messages"),
  createMessage: (text: string) => request<Reply>("POST", "/chat/messages", { text }),
  deleteMessages: () => request<void>("DELETE", "/chat/messages"),
}

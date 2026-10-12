import { useCallback, useEffect, useRef, useState } from "react"

import { api, ApiError } from "@/lib/api"
import { GREETING } from "@/presentation/constants/chat/constants"
import type { ChatMessage } from "@/presentation/types/chat/types"

type Options = {
  authVersion: number
  onUnauthorized: () => void
  onReplied: () => void
}

export function useChatPage({ authVersion, onUnauthorized, onReplied }: Options) {
  const nextId = useRef(0)
  const endRef = useRef<HTMLDivElement>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [busy, setBusy] = useState(false)

  const build = useCallback(
    (message: Omit<ChatMessage, "id">): ChatMessage => ({ ...message, id: nextId.current++ }),
    [],
  )

  const greet = useCallback(() => setMessages([build({ role: "assistant", text: GREETING })]), [build])

  const handleError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError && error.status === 401) return onUnauthorized()
      const text = error instanceof Error ? error.message : "Algo salió mal."
      setMessages((current) => [...current, build({ role: "error", text })])
    },
    [build, onUnauthorized],
  )

  const loadHistory = useCallback(async () => {
    try {
      const { messages: history } = await api.listMessages()
      if (!history.length) return greet()
      setMessages(history.map((message) => build({ role: message.role, text: message.content })))
    } catch (error) {
      greet()
      if (error instanceof ApiError && error.status === 401) onUnauthorized()
    }
  }, [build, greet, onUnauthorized])

  const handleSend = useCallback(
    async (text: string) => {
      setMessages((current) => [...current, build({ role: "user", text })])
      setBusy(true)
      try {
        const reply = await api.createMessage(text)
        setMessages((current) => [
          ...current,
          build({ role: "assistant", text: reply.text || "(sin respuesta)", tools: reply.tools_used, elapsed: reply.elapsed }),
        ])
      } catch (error) {
        handleError(error)
      } finally {
        setBusy(false)
        onReplied()
      }
    },
    [build, handleError, onReplied],
  )

  const handleReset = useCallback(async () => {
    try {
      await api.deleteMessages()
      greet()
    } catch (error) {
      handleError(error)
    }
  }, [greet, handleError])

  useEffect(() => {
    loadHistory()
  }, [loadHistory, authVersion])

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" })
  }, [messages, busy])

  return { messages, busy, endRef, handleSend, handleReset }
}

import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"

import { isDesktop } from "@/lib/desktop"
import { useSpeech } from "@/presentation/hooks/chat/useSpeech"
import { useHealth } from "@/presentation/hooks/layout/useHealth"
import { useSystemTheme } from "@/presentation/hooks/layout/useSystemTheme"
import type { ViewId } from "@/presentation/types/layout/types"

export function useAppShell() {
  useSystemTheme()
  const [view, setView] = useState<ViewId>("chat")
  const { health, online, refresh } = useHealth()
  const [authVersion, setAuthVersion] = useState(0)
  const speech = useSpeech()
  const voiceReady = Boolean(health?.services.voice?.reachable)

  const handleUnauthorized = useCallback(() => {
    setView("settings")
    toast.warning("Este servidor pide un token de acceso.")
  }, [])

  const handleTokenSaved = useCallback(() => {
    setAuthVersion((version) => version + 1)
    setView("chat")
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle("is-desktop", isDesktop)
  }, [])

  return { view, setView, health, online, refresh, authVersion, speech, voiceReady, handleUnauthorized, handleTokenSaved }
}

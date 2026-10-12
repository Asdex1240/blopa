import { useCallback, useState } from "react"
import { toast } from "sonner"

import type { MicrophoneState } from "@/presentation/types/chat/types"

export function useMicrophoneCheck() {
  const [state, setState] = useState<MicrophoneState>("unknown")

  const handleCheck = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      toast.warning("El micrófono solo funciona en la app de escritorio o en localhost.")
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach((track) => track.stop())
      setState("ready")
      toast.success("Micrófono listo. La voz llega en la fase 6.")
    } catch {
      setState("denied")
      toast.error("Sin permiso para usar el micrófono.")
    }
  }, [])

  return { state, handleCheck }
}

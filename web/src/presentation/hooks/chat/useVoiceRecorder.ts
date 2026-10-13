import { useCallback, useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { api } from "@/lib/api"
import { MAX_RECORDING_MS } from "@/presentation/constants/chat/constants"
import type { RecorderState } from "@/presentation/types/chat/types"

const MIME_TYPES = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"]

const supportedType = () => MIME_TYPES.find((type) => window.MediaRecorder?.isTypeSupported(type)) ?? ""

export function useVoiceRecorder(onText: (text: string) => void) {
  const [state, setState] = useState<RecorderState>("idle")
  const [seconds, setSeconds] = useState(0)
  const recorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const cancelled = useRef(false)
  const timers = useRef<number[]>([])

  const clearTimers = () => {
    timers.current.forEach((timer) => {
      window.clearTimeout(timer)
      window.clearInterval(timer)
    })
    timers.current = []
  }

  const transcribe = useCallback(
    async (audio: Blob) => {
      setState("transcribing")
      try {
        const { text } = await api.transcribe(audio)
        onText(text)
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "No pude entender el audio.")
      } finally {
        setState("idle")
      }
    },
    [onText],
  )

  const start = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      toast.warning("El micrófono solo funciona en la app de escritorio o en localhost.")
      return
    }
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } })
    } catch {
      toast.error("Sin permiso para usar el micrófono.")
      return
    }
    const type = supportedType()
    const media = new MediaRecorder(stream, type ? { mimeType: type } : undefined)
    chunks.current = []
    cancelled.current = false
    media.ondataavailable = (event) => event.data.size && chunks.current.push(event.data)
    media.onstop = () => {
      stream.getTracks().forEach((track) => track.stop())
      clearTimers()
      setSeconds(0)
      if (cancelled.current) return setState("idle")
      transcribe(new Blob(chunks.current, { type: media.mimeType || "audio/webm" }))
    }
    recorder.current = media
    media.start()
    setState("recording")
    timers.current.push(window.setInterval(() => setSeconds((value) => value + 1), 1000))
    timers.current.push(window.setTimeout(() => media.state === "recording" && media.stop(), MAX_RECORDING_MS))
  }, [transcribe])

  const stop = useCallback(() => {
    if (recorder.current?.state === "recording") recorder.current.stop()
  }, [])

  const cancel = useCallback(() => {
    cancelled.current = true
    stop()
  }, [stop])

  const toggle = useCallback(() => {
    if (state === "recording") stop()
    else if (state === "idle") start()
  }, [start, state, stop])

  useEffect(() => () => {
    cancelled.current = true
    if (recorder.current?.state === "recording") recorder.current.stop()
    clearTimers()
  }, [])

  return { state, seconds, toggle, stop, cancel }
}

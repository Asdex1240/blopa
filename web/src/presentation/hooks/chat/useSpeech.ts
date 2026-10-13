import { useCallback, useEffect, useState } from "react"

import { PREFERRED_VOICES, SPEAK_ALL_KEY } from "@/presentation/constants/chat/constants"
import { speakableText } from "@/presentation/utils/chat/speakableText"
import { storage } from "@/lib/storage"

const synth = () => (typeof window !== "undefined" ? window.speechSynthesis : undefined)

function pickVoice() {
  const voices = synth()?.getVoices() ?? []
  const spanish = voices.filter((voice) => voice.lang.toLowerCase().startsWith("es"))
  return (
    PREFERRED_VOICES.map((name) => spanish.find((voice) => voice.name.startsWith(name))).find(Boolean) ??
    spanish.find((voice) => voice.lang.toLowerCase() === "es-mx") ??
    spanish[0]
  )
}

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false)
  const [speakAll, setSpeakAllValue] = useState(() => storage.get(SPEAK_ALL_KEY) === "1")

  const setSpeakAll = (value: boolean) => {
    storage.set(SPEAK_ALL_KEY, value ? "1" : "0")
    setSpeakAllValue(value)
  }

  const stop = useCallback(() => {
    synth()?.cancel()
    setSpeaking(false)
  }, [])

  const speak = useCallback((text: string) => {
    const engine = synth()
    const clean = speakableText(text)
    if (!engine || !clean) return
    engine.cancel()
    const utterance = new SpeechSynthesisUtterance(clean)
    const voice = pickVoice()
    if (voice) utterance.voice = voice
    utterance.lang = voice?.lang ?? "es-MX"
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    setSpeaking(true)
    engine.speak(utterance)
  }, [])

  useEffect(() => {
    synth()?.getVoices()
    return () => synth()?.cancel()
  }, [])

  return { speaking, speakAll, setSpeakAll, speak, stop }
}

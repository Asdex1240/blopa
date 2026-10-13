import { useRef, useState, type FormEvent, type KeyboardEvent } from "react"

type Voice = { enabled: boolean; recording: boolean; toggle: () => void; cancel: () => void }

export function useComposer(busy: boolean, onSend: (text: string) => void, voice: Voice) {
  const [text, setText] = useState("")
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (event?: FormEvent) => {
    event?.preventDefault()
    const value = text.trim()
    if (!value || busy) return
    onSend(value)
    setText("")
    inputRef.current?.focus()
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Escape" && voice.recording) {
      event.preventDefault()
      voice.cancel()
      return
    }
    if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) return
    event.preventDefault()
    if (voice.recording || (voice.enabled && !text.trim() && !busy)) return voice.toggle()
    handleSubmit()
  }

  const canSend = !busy && text.trim().length > 0

  return { text, setText, inputRef, canSend, handleSubmit, handleKeyDown }
}

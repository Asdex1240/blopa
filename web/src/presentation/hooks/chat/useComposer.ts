import { useRef, useState, type FormEvent, type KeyboardEvent } from "react"

export function useComposer(busy: boolean, onSend: (text: string) => void) {
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
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) handleSubmit(event)
  }

  const canSend = !busy && text.trim().length > 0

  return { text, setText, inputRef, canSend, handleSubmit, handleKeyDown }
}

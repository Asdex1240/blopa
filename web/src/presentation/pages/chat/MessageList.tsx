import type { RefObject } from "react"

import type { ChatMessage as Message } from "@/presentation/types/chat/types"
import { ChatMessage } from "./ChatMessage"
import { ConfirmationActions, TypingIndicator } from "./Components"

type Props = {
  messages: Message[]
  busy: boolean
  confirmation: string | null
  endRef: RefObject<HTMLDivElement | null>
  onConfirm: () => void
  onCancel: () => void
}

export function MessageList({ messages, busy, confirmation, endRef, onConfirm, onCancel }: Props) {
  return (
    <div className="-mx-4 min-h-0 flex-1 overflow-y-auto px-4" aria-live="polite">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 py-2">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {confirmation && !busy && <ConfirmationActions onConfirm={onConfirm} onCancel={onCancel} />}
        {busy && <TypingIndicator />}
        <div ref={endRef} />
      </div>
    </div>
  )
}

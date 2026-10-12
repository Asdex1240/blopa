import type { RefObject } from "react"

import type { ChatMessage as Message } from "@/presentation/types/chat/types"
import { ChatMessage } from "./ChatMessage"
import { TypingIndicator } from "./Components"

type Props = { messages: Message[]; busy: boolean; endRef: RefObject<HTMLDivElement | null> }

export function MessageList({ messages, busy, endRef }: Props) {
  return (
    <div className="-mx-4 min-h-0 flex-1 overflow-y-auto px-4" aria-live="polite">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 py-2">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {busy && <TypingIndicator />}
        <div ref={endRef} />
      </div>
    </div>
  )
}

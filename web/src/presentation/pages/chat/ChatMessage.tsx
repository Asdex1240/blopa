import { CircleAlertIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import type { ChatMessage as Message } from "@/presentation/types/chat/types"
import { ToolBadge } from "./Components"

export function ChatMessage({ message }: { message: Message }) {
  const fromUser = message.role === "user"
  const isError = message.role === "error"
  const tools = [...new Set(message.tools ?? [])]
  const hasMeta = tools.length > 0 || message.elapsed !== undefined

  return (
    <div className={cn("flex max-w-[85%] flex-col gap-1.5 md:max-w-[min(680px,80%)]", fromUser ? "items-end self-end" : "self-start")}>
      <div
        className={cn(
          "rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed break-words whitespace-pre-wrap",
          fromUser && "rounded-br-md bg-primary text-primary-foreground",
          message.role === "assistant" && "rounded-bl-md border bg-card text-card-foreground",
          isError && "flex gap-2 rounded-bl-md border border-destructive/40 bg-destructive/10 text-destructive",
        )}
      >
        {isError && <CircleAlertIcon className="mt-0.5 size-4 shrink-0" />}
        {message.text}
      </div>
      {hasMeta && (
        <div className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
          {tools.map((tool) => (
            <ToolBadge key={tool} tool={tool} />
          ))}
          {message.elapsed !== undefined && <span>{message.elapsed} s</span>}
        </div>
      )}
    </div>
  )
}

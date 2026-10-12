import { CheckIcon, ShieldAlertIcon, XIcon } from "lucide-react"

import { TYPING_DELAYS_MS } from "@/presentation/constants/chat/constants"
import { toolInfo } from "@/presentation/utils/tools/toolInfo"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

export function TypingIndicator() {
  return (
    <div className="flex gap-1 self-start rounded-2xl rounded-bl-md border bg-card px-4 py-3.5" aria-label="BLOPA está escribiendo">
      {TYPING_DELAYS_MS.map((delay) => (
        <span
          key={delay}
          className="size-1.5 animate-pulse rounded-full bg-muted-foreground"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </div>
  )
}

export function ToolBadge({ tool }: { tool: string }) {
  const { action, icon: Icon } = toolInfo(tool)
  return (
    <Badge variant="secondary" className="gap-1">
      <Icon className="size-3" />
      {action}
    </Badge>
  )
}

type ConfirmationProps = { onConfirm: () => void; onCancel: () => void }

export function ConfirmationActions({ onConfirm, onCancel }: ConfirmationProps) {
  return (
    <div className="-mt-2 flex flex-wrap items-center gap-2 self-start">
      <span className="flex items-center gap-1.5 text-xs text-warning">
        <ShieldAlertIcon className="size-3.5" />
        Requiere confirmación
      </span>
      <Button size="sm" onClick={onConfirm}>
        <CheckIcon />
        Sí, hazlo
      </Button>
      <Button size="sm" variant="outline" onClick={onCancel}>
        <XIcon />
        No
      </Button>
    </div>
  )
}

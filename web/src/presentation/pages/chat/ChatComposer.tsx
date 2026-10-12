import { ArrowUpIcon, MicIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { MIC_COLOR } from "@/presentation/constants/chat/constants"
import { useComposer } from "@/presentation/hooks/chat/useComposer"
import { useMicrophoneCheck } from "@/presentation/hooks/chat/useMicrophoneCheck"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

export function ChatComposer({ busy, onSend }: { busy: boolean; onSend: (text: string) => void }) {
  const { text, setText, inputRef, canSend, handleSubmit, handleKeyDown } = useComposer(busy, onSend)
  const microphone = useMicrophoneCheck()

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-3xl pb-[env(safe-area-inset-bottom)]">
      <div className="flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-xs focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/20">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button type="button" variant="ghost" size="icon-lg" onClick={microphone.handleCheck} aria-label="Probar micrófono">
              <MicIcon className={cn(MIC_COLOR[microphone.state])} />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Probar micrófono</TooltipContent>
        </Tooltip>
        <Textarea
          ref={inputRef}
          autoFocus
          rows={1}
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un mensaje…"
          className="max-h-40 min-h-9 resize-none border-0 bg-transparent px-1 py-2 shadow-none focus-visible:ring-0 dark:bg-transparent"
        />
        <Button type="submit" size="icon-lg" disabled={!canSend} aria-label="Enviar">
          <ArrowUpIcon />
        </Button>
      </div>
    </form>
  )
}

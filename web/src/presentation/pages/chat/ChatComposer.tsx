import { ArrowUpIcon, Loader2Icon, MicIcon, SquareIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { useComposer } from "@/presentation/hooks/chat/useComposer"
import { useVoiceRecorder } from "@/presentation/hooks/chat/useVoiceRecorder"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

type Props = {
  busy: boolean
  voiceEnabled: boolean
  onSend: (text: string) => void
  onVoiceText: (text: string) => void
}

const clock = (seconds: number) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`

export function ChatComposer({ busy, voiceEnabled, onSend, onVoiceText }: Props) {
  const recorder = useVoiceRecorder(onVoiceText)
  const recording = recorder.state === "recording"
  const transcribing = recorder.state === "transcribing"
  const { text, setText, inputRef, canSend, handleSubmit, handleKeyDown } = useComposer(busy, onSend, {
    enabled: voiceEnabled,
    recording,
    toggle: recorder.toggle,
    cancel: recorder.cancel,
  })

  const placeholder = recording
    ? `Escuchando… ${clock(recorder.seconds)} · Enter para enviar, Esc para cancelar`
    : transcribing
      ? "Entendiendo lo que dijiste…"
      : voiceEnabled
        ? "Escribe un mensaje o presiona Enter para hablar…"
        : "Escribe un mensaje…"

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-3xl pb-[env(safe-area-inset-bottom)]">
      <div
        className={cn(
          "flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-xs focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/20",
          recording && "border-destructive/60 focus-within:border-destructive/60 focus-within:ring-destructive/20",
        )}
      >
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant={recording ? "destructive" : "ghost"}
              size="icon-lg"
              onClick={recorder.toggle}
              disabled={!voiceEnabled || transcribing || busy}
              aria-label={recording ? "Terminar y enviar" : "Hablar"}
            >
              {transcribing ? (
                <Loader2Icon className="animate-spin" />
              ) : recording ? (
                <SquareIcon className="animate-pulse fill-current" />
              ) : (
                <MicIcon />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {voiceEnabled ? (recording ? "Terminar y enviar (Enter)" : "Hablar (Enter con el cuadro vacío)") : "El servicio de voz no está disponible"}
          </TooltipContent>
        </Tooltip>
        <Textarea
          ref={inputRef}
          autoFocus
          rows={1}
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          readOnly={recording || transcribing}
          className="max-h-40 min-h-9 resize-none border-0 bg-transparent px-1 py-2 shadow-none focus-visible:ring-0 dark:bg-transparent"
        />
        <Button type="submit" size="icon-lg" disabled={!canSend} aria-label="Enviar">
          <ArrowUpIcon />
        </Button>
      </div>
    </form>
  )
}

import { Volume2Icon } from "lucide-react"

import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import type { Health } from "@/presentation/types/api/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

type Props = {
  health: Health | null
  speakAll: boolean
  onSpeakAllChange: (value: boolean) => void
  onTestVoice: () => void
}

function transcriptionStatus(health: Health | null) {
  const voice = health?.services.voice
  if (!voice?.configured) return "No configurado"
  if (!voice.reachable) return "Configurado, pero no responde"
  return voice.ready ? `Listo (modelo ${voice.model})` : `Cargando modelo ${voice.model}…`
}

export function VoiceSettings({ health, speakAll, onSpeakAllChange, onTestVoice }: Props) {
  return (
    <Card>
      <CardContent className="grid gap-4">
        <SectionTitle>Voz</SectionTitle>
        <p className="-mt-2 text-sm text-muted-foreground">
          Reconocimiento de voz: <span className="text-foreground">{transcriptionStatus(health)}</span>
        </p>
        <div className="flex items-start justify-between gap-4 rounded-lg border p-3">
          <div className="space-y-1">
            <Label htmlFor="speak-all" className="text-xs font-medium">
              Leer en voz alta todas las respuestas
            </Label>
            <p className="text-xs text-muted-foreground">
              Cuando hablas, BLOPA siempre te responde en voz alta. Activa esto para que también lea las respuestas a lo
              que escribes.
            </p>
          </div>
          <Switch id="speak-all" checked={speakAll} onCheckedChange={onSpeakAllChange} />
        </div>
        <Button variant="outline" className="h-9 justify-self-start" onClick={onTestVoice}>
          <Volume2Icon />
          Probar voz
        </Button>
      </CardContent>
    </Card>
  )
}

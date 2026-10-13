import { CircleCheckIcon, Loader2Icon } from "lucide-react"

import type { NewDeviceName } from "@/presentation/types/devices/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Props = {
  names: NewDeviceName[]
  looking: boolean
  saving: boolean
  onNameChange: (entityId: string, name: string) => void
  onSave: () => void
}

export function NameDevicesStep({ names, looking, saving, onNameChange, onSave }: Props) {
  if (looking) {
    return (
      <p className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
        <Loader2Icon className="size-4 animate-spin" />
        Buscando tus dispositivos…
      </p>
    )
  }

  return (
    <div className="grid gap-4">
      <p className="flex items-start gap-2 text-sm">
        <CircleCheckIcon className="mt-0.5 size-4 shrink-0 text-success" />
        {names.length
          ? "¡Conectado! ¿Cómo le dices a cada uno? Usa el nombre con el que se lo pedirías a BLOPA."
          : "Conectado, pero todavía no aparecen dispositivos nuevos. Pueden tardar un minuto; después cámbiales el nombre con el lápiz."}
      </p>
      {names.map((item) => (
        <div key={item.entity_id} className="space-y-1.5">
          <Label htmlFor={`name-${item.entity_id}`} className="text-xs font-medium">
            {item.original}
          </Label>
          <Input
            id={`name-${item.entity_id}`}
            value={item.name}
            onChange={(event) => onNameChange(item.entity_id, event.target.value)}
            placeholder="Luz del cuarto"
            className="h-9 bg-background"
          />
        </div>
      ))}
      <Button onClick={onSave} disabled={saving}>
        {saving && <Loader2Icon className="animate-spin" />}
        Terminar
      </Button>
    </div>
  )
}

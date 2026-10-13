import { CircleAlertIcon, Loader2Icon, RadarIcon } from "lucide-react"

import { useMatterPairing } from "@/presentation/hooks/devices/useMatterPairing"
import { FieldError } from "@/presentation/pages/shared/FieldError"
import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import { StepList } from "./Components"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Props = { steps: string[]; onPaired: () => void }

export function MatterStep({ steps, onPaired }: Props) {
  const { code, error, discovered, searching, pairing, failure, setCode, handleSubmit } = useMatterPairing(onPaired)

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <StepList steps={steps} />
      <div>
        <SectionTitle>Encontrados en la red</SectionTitle>
        {discovered.length === 0 ? (
          <p className="flex items-start gap-2 rounded-lg border border-dashed p-3 text-xs text-muted-foreground">
            {searching ? <Loader2Icon className="mt-0.5 size-3.5 shrink-0 animate-spin" /> : <RadarIcon className="mt-0.5 size-3.5 shrink-0" />}
            Cuando generes el código, el dispositivo aparecerá aquí. Esta lista se actualiza sola.
          </p>
        ) : (
          <ul className="grid gap-2">
            {discovered.map((device) => (
              <li key={device.id} className="flex items-center gap-3 rounded-lg border p-3">
                <RadarIcon className="size-4 shrink-0 text-success" />
                <span className="truncate text-sm font-medium">{device.name}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="pairing-code" className="text-xs font-medium">
          Código para compartir
        </Label>
        <Input
          id="pairing-code"
          value={code}
          onChange={(event) => setCode(event.target.value)}
          placeholder="1234-567-8901"
          inputMode="numeric"
          autoComplete="off"
          aria-invalid={Boolean(error)}
          className="h-9 bg-background font-mono"
        />
        <FieldError message={error} />
      </div>
      {failure && (
        <p className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
          <CircleAlertIcon className="mt-0.5 size-3.5 shrink-0" />
          {failure}
        </p>
      )}
      <Button type="submit" disabled={pairing}>
        {pairing && <Loader2Icon className="animate-spin" />}
        {pairing ? "Emparejando… puede tardar 2 minutos" : "Emparejar"}
      </Button>
    </form>
  )
}

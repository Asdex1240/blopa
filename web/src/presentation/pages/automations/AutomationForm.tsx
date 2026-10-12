import { Loader2Icon } from "lucide-react"

import { WEBHOOK_PREFIX } from "@/presentation/constants/automations/constants"
import { useAutomationForm } from "@/presentation/hooks/automations/useAutomationForm"
import type { Automation, AutomationInput } from "@/presentation/types/automations/types"
import { FieldError } from "./Components"
import { Button } from "@/components/ui/button"
import { DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"

type Props = {
  automation: Automation | null
  onCancel: () => void
  onSave: (input: AutomationInput) => Promise<boolean>
}

export function AutomationForm({ automation, onCancel, onSave }: Props) {
  const { values, errors, saving, setField, handleSubmit } = useAutomationForm(automation, onSave)

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="space-y-1.5">
        <Label htmlFor="automation-name" className="text-xs font-medium">
          Nombre
        </Label>
        <Input
          id="automation-name"
          value={values.name}
          onChange={(event) => setField("name", event.target.value)}
          placeholder="Ping de prueba"
          aria-invalid={Boolean(errors.name)}
          className="h-9 bg-background"
        />
        <FieldError message={errors.name} />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="automation-description" className="text-xs font-medium">
          Descripción
        </Label>
        <Textarea
          id="automation-description"
          value={values.description}
          onChange={(event) => setField("description", event.target.value)}
          placeholder="Qué hace el flujo. BLOPA la usa para saber cuándo lanzarla."
          aria-invalid={Boolean(errors.description)}
          className="min-h-20 bg-background"
        />
        <FieldError message={errors.description} />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="automation-webhook" className="text-xs font-medium">
          Ruta del webhook
        </Label>
        <div className="flex items-center gap-2">
          <span className="shrink-0 font-mono text-xs text-muted-foreground">{WEBHOOK_PREFIX}</span>
          <Input
            id="automation-webhook"
            value={values.webhook_path}
            onChange={(event) => setField("webhook_path", event.target.value)}
            placeholder="blopa-ping"
            aria-invalid={Boolean(errors.webhook_path)}
            className="h-9 bg-background font-mono"
          />
        </div>
        <FieldError message={errors.webhook_path} />
      </div>
      <div className="flex items-start justify-between gap-4 rounded-lg border p-3">
        <div className="space-y-1">
          <Label htmlFor="automation-confirmation" className="text-xs font-medium">
            Pedir confirmación
          </Label>
          <p className="text-xs text-muted-foreground">BLOPA describe la acción y espera tu "sí" antes de ejecutarla.</p>
        </div>
        <Switch
          id="automation-confirmation"
          checked={values.requires_confirmation}
          onCheckedChange={(checked) => setField("requires_confirmation", checked)}
        />
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" disabled={saving}>
          {saving && <Loader2Icon className="animate-spin" />}
          {automation ? "Guardar cambios" : "Crear automatización"}
        </Button>
      </DialogFooter>
    </form>
  )
}

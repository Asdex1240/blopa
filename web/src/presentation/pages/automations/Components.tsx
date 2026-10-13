import { CircleCheckIcon, CircleXIcon, PlugZapIcon, WorkflowIcon } from "lucide-react"

import type { AutomationRun } from "@/presentation/types/automations/types"
import { formatDate } from "@/presentation/utils/automations/formatDate"
import { Badge } from "@/components/ui/badge"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function RunStatusBadge({ run }: { run: AutomationRun }) {
  return run.ok ? (
    <Badge variant="secondary" className="gap-1 text-success">
      <CircleCheckIcon className="size-3" />
      Correcta
    </Badge>
  ) : (
    <Badge variant="secondary" className="gap-1 text-destructive">
      <CircleXIcon className="size-3" />
      Falló
    </Badge>
  )
}

export function LastRun({ run }: { run: AutomationRun | null }) {
  if (!run) return <span className="text-xs text-muted-foreground">Nunca</span>
  return (
    <div className="flex flex-col items-start gap-1">
      <RunStatusBadge run={run} />
      <span className="text-xs text-muted-foreground">{formatDate(run.started_at)}</span>
    </div>
  )
}

export function EmptyAutomations() {
  return (
    <div className="flex flex-col items-center gap-2 py-10 text-center">
      <div className="flex size-10 items-center justify-center rounded-lg bg-muted">
        <WorkflowIcon className="size-5 text-muted-foreground" />
      </div>
      <p className="text-sm font-medium">Aún no hay automatizaciones</p>
      <p className="max-w-sm text-sm text-muted-foreground">
        Crea un flujo con un nodo Webhook en n8n y regístralo aquí para que BLOPA pueda lanzarlo.
      </p>
    </div>
  )
}

export function N8nUnavailable() {
  return (
    <Card>
      <CardHeader>
        <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-muted">
          <PlugZapIcon className="size-5 text-muted-foreground" />
        </div>
        <CardTitle>n8n no está configurado</CardTitle>
        <CardDescription>Define N8N_URL en el archivo .env y activa el perfil n8n para usar automatizaciones.</CardDescription>
      </CardHeader>
    </Card>
  )
}

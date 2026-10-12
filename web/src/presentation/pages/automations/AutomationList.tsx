import { Loader2Icon, PencilIcon, PlayIcon, ShieldCheckIcon, Trash2Icon, ZapIcon } from "lucide-react"

import type { Automation } from "@/presentation/types/automations/types"
import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import { EmptyAutomations, LastRun } from "./Components"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

type Props = {
  automations: Automation[]
  loading: boolean
  runningId: number | null
  onRun: (automation: Automation) => void
  onEdit: (automation: Automation) => void
  onDelete: (automation: Automation) => void
}

export function AutomationList({ automations, loading, runningId, onRun, onEdit, onDelete }: Props) {
  return (
    <Card>
      <CardContent>
        <SectionTitle>Automatizaciones registradas</SectionTitle>
        {!loading && automations.length === 0 ? (
          <EmptyAutomations />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead className="hidden md:table-cell">Webhook</TableHead>
                <TableHead className="hidden md:table-cell">Modo</TableHead>
                <TableHead className="hidden sm:table-cell">Última ejecución</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {automations.map((automation) => (
                <TableRow key={automation.id}>
                  <TableCell className="min-w-40 max-w-72 whitespace-normal">
                    <p className="font-medium">{automation.name}</p>
                    <p className="text-xs text-muted-foreground">{automation.description}</p>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
                    <code className="font-mono text-xs">/webhook/{automation.webhook_path}</code>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
                    {automation.requires_confirmation ? (
                      <Badge variant="secondary" className="gap-1">
                        <ShieldCheckIcon className="size-3" />
                        Pide confirmación
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="gap-1">
                        <ZapIcon className="size-3" />
                        Directa
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <LastRun run={automation.last_run} />
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => onRun(automation)}
                            disabled={runningId !== null}
                            aria-label={`Ejecutar ${automation.name}`}
                          >
                            {runningId === automation.id ? <Loader2Icon className="animate-spin" /> : <PlayIcon />}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Ejecutar ahora</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="icon" onClick={() => onEdit(automation)} aria-label={`Editar ${automation.name}`}>
                            <PencilIcon />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Editar</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => onDelete(automation)}
                            aria-label={`Eliminar ${automation.name}`}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2Icon />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Eliminar</TooltipContent>
                      </Tooltip>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}

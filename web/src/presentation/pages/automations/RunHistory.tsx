import { MessageCircleIcon, MousePointerClickIcon } from "lucide-react"

import { SOURCE_LABELS } from "@/presentation/constants/automations/constants"
import type { AutomationRun } from "@/presentation/types/automations/types"
import { formatDate } from "@/presentation/utils/automations/formatDate"
import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import { RunStatusBadge } from "./Components"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export function RunHistory({ runs }: { runs: AutomationRun[] }) {
  return (
    <Card>
      <CardContent>
        <SectionTitle>Historial de ejecuciones</SectionTitle>
        {runs.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">Todavía no se ha ejecutado ninguna automatización.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead className="hidden sm:table-cell">Automatización</TableHead>
                <TableHead className="hidden md:table-cell">Origen</TableHead>
                <TableHead>Resultado</TableHead>
                <TableHead className="hidden text-right md:table-cell">Duración</TableHead>
                <TableHead className="hidden lg:table-cell">Detalle</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => {
                const SourceIcon = run.source === "chat" ? MessageCircleIcon : MousePointerClickIcon
                return (
                  <TableRow key={run.id}>
                    <TableCell className="text-xs text-muted-foreground">{formatDate(run.started_at)}</TableCell>
                    <TableCell className="hidden font-medium sm:table-cell">{run.automation_name}</TableCell>
                    <TableCell className="hidden md:table-cell">
                      <span className="flex items-center gap-1.5 text-xs">
                        <SourceIcon className="size-3.5 text-muted-foreground" />
                        {SOURCE_LABELS[run.source]}
                      </span>
                    </TableCell>
                    <TableCell>
                      <RunStatusBadge run={run} />
                    </TableCell>
                    <TableCell className="hidden text-right text-xs tabular-nums md:table-cell">{run.duration_ms} ms</TableCell>
                    <TableCell className="hidden max-w-64 truncate font-mono text-xs text-muted-foreground lg:table-cell" title={run.detail}>
                      {run.detail || "—"}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}

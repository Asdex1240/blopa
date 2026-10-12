import { isDesktop } from "@/lib/desktop"
import type { Health } from "@/presentation/types/api/types"
import { modelState } from "@/presentation/utils/settings/modelState"
import { toolInfo } from "@/presentation/utils/tools/toolInfo"
import { SectionTitle, SettingRow } from "./Components"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

export function SystemDetails({ health }: { health: Health | null }) {
  return (
    <Card>
      <CardContent>
        <SectionTitle>Sistema</SectionTitle>
        {health ? (
          <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-3 text-sm">
            <SettingRow label="Modelo">
              <code className="font-mono text-xs">{health.model}</code>
            </SettingRow>
            <SettingRow label="Estado del modelo">{modelState(health)}</SettingRow>
            <SettingRow label="Zona horaria">{health.timezone}</SettingRow>
            <SettingRow label="Herramientas">
              <span className="flex flex-wrap gap-1.5">
                {health.tools.map((tool) => {
                  const { name, icon: Icon } = toolInfo(tool)
                  return (
                    <Badge key={tool} variant="secondary" className="gap-1">
                      <Icon className="size-3" />
                      {name}
                    </Badge>
                  )
                })}
              </span>
            </SettingRow>
            <SettingRow label="Acceso">{health.auth_required ? "Protegido con token" : "Abierto en la red local"}</SettingRow>
            <SettingRow label="Aplicación">{isDesktop ? "Escritorio (Electron)" : "Navegador"}</SettingRow>
          </dl>
        ) : (
          <p className="text-sm text-muted-foreground">Sin conexión con el servidor.</p>
        )}
      </CardContent>
    </Card>
  )
}

import { HouseIcon } from "lucide-react"

import type { Device, DeviceAction, DeviceGroup as Group } from "@/presentation/types/devices/types"
import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import { DeviceCard } from "./DeviceCard"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

type GroupProps = {
  group: Group
  busyId: string | null
  onAction: (request: DeviceAction) => void
  onRename: (device: Device) => void
}

export function DeviceGroup({ group, busyId, onAction, onRename }: GroupProps) {
  return (
    <section>
      <SectionTitle>{group.title}</SectionTitle>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {group.devices.map((device) => (
          <DeviceCard
            key={device.entity_id}
            device={device}
            busy={busyId === device.entity_id}
            onAction={onAction}
            onRename={onRename}
          />
        ))}
      </div>
    </section>
  )
}

export function HomeAssistantUnavailable() {
  return (
    <Card>
      <CardHeader>
        <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-muted">
          <HouseIcon className="size-5 text-muted-foreground" />
        </div>
        <CardTitle>Home Assistant no está configurado</CardTitle>
        <CardDescription>Define HA_URL y HA_TOKEN en el archivo .env y activa el perfil home.</CardDescription>
      </CardHeader>
    </Card>
  )
}

export function EmptyDevices() {
  return (
    <p className="py-10 text-center text-sm text-muted-foreground">
      Todavía no hay dispositivos. Usa «Agregar» para conectar el primero.
    </p>
  )
}

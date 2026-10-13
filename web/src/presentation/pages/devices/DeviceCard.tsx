import { Loader2Icon, MinusIcon, PencilIcon, PlusIcon, ShieldAlertIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { ACTION_LABELS, DOMAIN_ICONS, TEMPERATURE_STEP, TOGGLE_DOMAINS } from "@/presentation/constants/devices/constants"
import type { Device, DeviceAction } from "@/presentation/types/devices/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

type Props = { device: Device; busy: boolean; onAction: (request: DeviceAction) => void }

type CardProps = Props & { onRename: (device: Device) => void }

function ToggleControl({ device, busy, onAction }: Props) {
  const on = device.state === "on"
  return (
    <Switch
      checked={on}
      disabled={busy || device.state === "unavailable"}
      onCheckedChange={(checked) => onAction({ device, action: checked ? "encender" : "apagar" })}
      aria-label={`${on ? "Apagar" : "Encender"} ${device.name}`}
    />
  )
}

function TemperatureControl({ device, busy, onAction }: Props) {
  const target = device.attributes.temperature
  if (target === undefined) return null
  const change = (delta: number) => onAction({ device, action: "ajustar_temperatura", value: target + delta })
  return (
    <div className="flex items-center gap-1">
      <Button variant="outline" size="icon-sm" disabled={busy} onClick={() => change(-TEMPERATURE_STEP)} aria-label="Bajar temperatura">
        <MinusIcon />
      </Button>
      <span className="w-14 text-center text-sm font-medium tabular-nums">{target} °C</span>
      <Button variant="outline" size="icon-sm" disabled={busy} onClick={() => change(TEMPERATURE_STEP)} aria-label="Subir temperatura">
        <PlusIcon />
      </Button>
    </div>
  )
}

function ActionButtons({ device, busy, onAction }: Props) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {device.actions.map((action) => (
        <Button key={action} variant="outline" size="sm" disabled={busy} onClick={() => onAction({ device, action })}>
          {ACTION_LABELS[action] ?? action}
        </Button>
      ))}
    </div>
  )
}

function Controls(props: Props) {
  if (TOGGLE_DOMAINS.has(props.device.domain)) return <ToggleControl {...props} />
  if (props.device.domain === "climate") return <TemperatureControl {...props} />
  return <ActionButtons {...props} />
}

export function DeviceCard({ device, busy, onAction, onRename }: CardProps) {
  const Icon = DOMAIN_ICONS[device.domain]
  const active = ["on", "open", "unlocked"].includes(device.state)
  const problem = device.state === "jammed" || device.state === "unavailable"
  const toggle = TOGGLE_DOMAINS.has(device.domain)

  return (
    <Card size="sm" className={cn(problem && "ring-destructive/40")}>
      <CardContent className="flex flex-col gap-3">
        <div className={cn("flex justify-between gap-3", toggle ? "items-center" : "items-start")}>
          <div className="flex min-w-0 items-center gap-3">
            <div
              className={cn(
                "flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground",
                active && "bg-primary/15 text-primary",
                problem && "bg-destructive/10 text-destructive",
              )}
            >
              {busy ? <Loader2Icon className="size-4 animate-spin" /> : <Icon className="size-4" />}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1">
                <p className="truncate text-sm font-medium">{device.name}</p>
                <Button
                  variant="ghost"
                  size="icon-xs"
                  onClick={() => onRename(device)}
                  aria-label={`Cambiar nombre de ${device.name}`}
                  className="text-muted-foreground"
                >
                  <PencilIcon />
                </Button>
              </div>
              <p className={cn("text-xs text-muted-foreground", problem && "text-destructive")}>{device.state_label}</p>
            </div>
          </div>
          {toggle && <Controls device={device} busy={busy} onAction={onAction} />}
          {device.sensitive && (
            <Tooltip>
              <TooltipTrigger asChild>
                <ShieldAlertIcon className="size-4 shrink-0 text-warning" tabIndex={0} aria-label="Pide confirmación" />
              </TooltipTrigger>
              <TooltipContent>Pide confirmación antes de actuar</TooltipContent>
            </Tooltip>
          )}
        </div>
        {!toggle && <Controls device={device} busy={busy} onAction={onAction} />}
      </CardContent>
    </Card>
  )
}

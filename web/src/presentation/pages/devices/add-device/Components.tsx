import { ChevronRightIcon, HouseWifiIcon, ShieldCheckIcon, SmartphoneIcon, SpeakerIcon, StoreIcon, type LucideIcon } from "lucide-react"

import { SOURCE_OPTIONS } from "@/presentation/constants/devices/constants"
import type { DeviceSource } from "@/presentation/types/devices/types"

const SOURCE_ICONS: Record<DeviceSource, LucideIcon> = {
  smartlife: SmartphoneIcon,
  generic: StoreIcon,
  alexa: SpeakerIcon,
  google: HouseWifiIcon,
  "matter-code": ShieldCheckIcon,
}

type SourceProps = { matterEnabled: boolean; onSelect: (source: DeviceSource) => void }

export function SourceStep({ matterEnabled, onSelect }: SourceProps) {
  return (
    <div className="grid gap-2">
      <p className="text-sm font-medium">¿Con qué app lo controlas hoy?</p>
      {SOURCE_OPTIONS.filter((option) => matterEnabled || !option.matter).map((option) => {
        const Icon = SOURCE_ICONS[option.id]
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => onSelect(option.id)}
            className="flex items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-muted"
          >
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted">
              <Icon className="size-4 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">{option.title}</p>
              <p className="text-xs text-muted-foreground">{option.description}</p>
            </div>
            <ChevronRightIcon className="size-4 shrink-0 text-muted-foreground" />
          </button>
        )
      })}
    </div>
  )
}

export function StepList({ steps }: { steps: string[] }) {
  return (
    <ol className="grid gap-2">
      {steps.map((step, index) => (
        <li key={step} className="flex gap-2.5 text-sm">
          <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-medium text-primary">
            {index + 1}
          </span>
          <span className="text-muted-foreground">{step}</span>
        </li>
      ))}
    </ol>
  )
}

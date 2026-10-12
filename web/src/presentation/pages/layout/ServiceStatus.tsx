import { cn } from "@/lib/utils"
import { SERVICE_DOT } from "@/presentation/constants/layout/constants"
import type { Health } from "@/presentation/types/api/types"
import { buildServices } from "@/presentation/utils/layout/services"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

type Props = { health: Health | null; online: boolean; compact?: boolean }

export function ServiceStatus({ health, online, compact }: Props) {
  return (
    <ul className={cn("flex gap-2 text-xs text-muted-foreground", compact ? "flex-row" : "flex-col")}>
      {buildServices(health, online).map((service) => (
        <li key={service.label}>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-2" tabIndex={0}>
                <span className={cn("size-2 shrink-0 rounded-full", SERVICE_DOT[service.state])} />
                <span className={cn(compact && "sr-only")}>{service.label}</span>
              </span>
            </TooltipTrigger>
            <TooltipContent side={compact ? "bottom" : "right"}>
              {service.label}: {service.detail}
            </TooltipContent>
          </Tooltip>
        </li>
      ))}
    </ul>
  )
}

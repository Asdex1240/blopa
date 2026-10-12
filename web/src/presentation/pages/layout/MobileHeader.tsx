import { cn } from "@/lib/utils"
import { VIEWS } from "@/presentation/constants/layout/constants"
import type { Health } from "@/presentation/types/api/types"
import type { ViewId } from "@/presentation/types/layout/types"
import { Brand } from "./Components"
import { ServiceStatus } from "./ServiceStatus"

type Props = {
  view: ViewId
  onSelect: (view: ViewId) => void
  health: Health | null
  online: boolean
}

export function MobileHeader({ view, onSelect, health, online }: Props) {
  return (
    <header className="flex flex-col gap-2 border-b bg-sidebar px-4 pt-3 pb-2 md:hidden">
      <div className="flex items-center justify-between">
        <Brand />
        <ServiceStatus health={health} online={online} compact />
      </div>
      <nav className="-mx-1 flex gap-1 overflow-x-auto [scrollbar-width:none]" aria-label="Secciones">
        {VIEWS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onSelect(id)}
            aria-current={view === id ? "page" : undefined}
            className={cn(
              "flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm text-muted-foreground",
              view === id && "bg-sidebar-accent font-medium text-sidebar-accent-foreground",
            )}
          >
            <Icon className="size-3.5" />
            {label}
          </button>
        ))}
      </nav>
    </header>
  )
}

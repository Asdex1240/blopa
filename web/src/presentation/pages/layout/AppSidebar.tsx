import { cn } from "@/lib/utils"
import { VIEWS } from "@/presentation/constants/layout/constants"
import type { Health } from "@/presentation/types/api/types"
import type { ViewId } from "@/presentation/types/layout/types"
import { Brand } from "./Components"
import { ServiceStatus } from "./ServiceStatus"
import { Separator } from "@/components/ui/separator"

type Props = {
  view: ViewId
  onSelect: (view: ViewId) => void
  health: Health | null
  online: boolean
}

export function AppSidebar({ view, onSelect, health, online }: Props) {
  return (
    <aside className="app-drag hidden w-56 shrink-0 flex-col gap-6 border-r bg-sidebar px-3 py-5 text-sidebar-foreground md:flex desktop:pt-12">
      <div className="px-2">
        <Brand />
      </div>
      <nav className="flex flex-col gap-0.5" aria-label="Secciones">
        {VIEWS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onSelect(id)}
            aria-current={view === id ? "page" : undefined}
            className={cn(
              "app-no-drag flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              view === id && "bg-sidebar-accent font-medium text-sidebar-accent-foreground",
            )}
          >
            <Icon className="size-4" />
            {label}
          </button>
        ))}
      </nav>
      <div className="mt-auto flex flex-col gap-3 px-2">
        <Separator />
        <ServiceStatus health={health} online={online} />
      </div>
    </aside>
  )
}

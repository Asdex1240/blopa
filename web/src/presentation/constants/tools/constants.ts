import { CalendarClockIcon, FileTextIcon, GlobeIcon, WorkflowIcon } from "lucide-react"

import type { ToolInfo } from "@/presentation/types/tools/types"

export const TOOLS: Record<string, ToolInfo> = {
  search_web: { action: "Buscó en internet", name: "Búsqueda web", icon: GlobeIcon },
  read_page: { action: "Leyó una página", name: "Lectura de páginas", icon: FileTextIcon },
  date_time: { action: "Consultó la hora", name: "Fecha y hora", icon: CalendarClockIcon },
  run_automation: { action: "Ejecutó una automatización", name: "Automatizaciones n8n", icon: WorkflowIcon },
}

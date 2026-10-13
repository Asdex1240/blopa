import { CalendarClockIcon, FileTextIcon, GlobeIcon, HouseIcon, ListIcon, SlidersHorizontalIcon, WorkflowIcon } from "lucide-react"

import type { ToolInfo } from "@/presentation/types/tools/types"

export const TOOLS: Record<string, ToolInfo> = {
  search_web: { action: "Buscó en internet", name: "Búsqueda web", icon: GlobeIcon },
  read_page: { action: "Leyó una página", name: "Lectura de páginas", icon: FileTextIcon },
  date_time: { action: "Consultó la hora", name: "Fecha y hora", icon: CalendarClockIcon },
  run_automation: { action: "Ejecutó una automatización", name: "Automatizaciones n8n", icon: WorkflowIcon },
  home_list_devices: { action: "Revisó la casa", name: "Lista de dispositivos", icon: ListIcon },
  home_device_status: { action: "Consultó un dispositivo", name: "Estado de dispositivos", icon: HouseIcon },
  home_control_device: { action: "Controló un dispositivo", name: "Control de la casa", icon: SlidersHorizontalIcon },
}

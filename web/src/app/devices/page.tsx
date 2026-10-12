import { HouseIcon } from "lucide-react"

import { ComingSoon } from "@/presentation/pages/shared/ComingSoon"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"

export default function DevicesPage() {
  return (
    <div className="flex flex-col gap-4 pb-6">
      <PageHeader title="Dispositivos" />
      <ComingSoon icon={HouseIcon} description="Aquí aparecerán las luces y enchufes de Home Assistant." phase={5} />
    </div>
  )
}

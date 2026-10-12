import { WorkflowIcon } from "lucide-react"

import { ComingSoon } from "@/presentation/pages/shared/ComingSoon"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"

export default function AutomationsPage() {
  return (
    <div className="flex flex-col gap-4 pb-6">
      <PageHeader title="Automatizaciones" />
      <ComingSoon icon={WorkflowIcon} description="Aquí podrás crear y lanzar flujos de n8n." phase={4} />
    </div>
  )
}

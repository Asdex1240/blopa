import { PlusIcon } from "lucide-react"

import { useAutomationsPage } from "@/presentation/hooks/automations/useAutomationsPage"
import { AutomationFormDialog } from "@/presentation/pages/automations/AutomationFormDialog"
import { AutomationList } from "@/presentation/pages/automations/AutomationList"
import { N8nUnavailable } from "@/presentation/pages/automations/Components"
import { DeleteAutomationDialog } from "@/presentation/pages/automations/DeleteAutomationDialog"
import { RunHistory } from "@/presentation/pages/automations/RunHistory"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"
import { Button } from "@/components/ui/button"

type Props = { n8nConfigured: boolean; onUnauthorized: () => void }

export default function AutomationsPage({ n8nConfigured, onUnauthorized }: Props) {
  const {
    automations,
    runs,
    loading,
    formOpen,
    editing,
    deleting,
    runningId,
    setFormOpen,
    setDeleting,
    handleCreate,
    handleEdit,
    handleSave,
    handleDelete,
    handleRun,
  } = useAutomationsPage({ enabled: n8nConfigured, onUnauthorized })

  if (!n8nConfigured) {
    return (
      <div className="flex flex-col gap-4 pb-6">
        <PageHeader title="Automatizaciones" />
        <N8nUnavailable />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 pb-6">
      <PageHeader title="Automatizaciones">
        <Button onClick={handleCreate}>
          <PlusIcon />
          Nueva
        </Button>
      </PageHeader>
      <AutomationList
        automations={automations}
        loading={loading}
        runningId={runningId}
        onRun={handleRun}
        onEdit={handleEdit}
        onDelete={setDeleting}
      />
      <RunHistory runs={runs} />
      <AutomationFormDialog open={formOpen} automation={editing} onOpenChange={setFormOpen} onSave={handleSave} />
      <DeleteAutomationDialog automation={deleting} onCancel={() => setDeleting(null)} onConfirm={handleDelete} />
    </div>
  )
}

import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"

import { api, ApiError } from "@/lib/api"
import { RUN_HISTORY_LIMIT } from "@/presentation/constants/automations/constants"
import type { Automation, AutomationInput, AutomationRun } from "@/presentation/types/automations/types"

type Options = { enabled: boolean; onUnauthorized: () => void }

export function useAutomationsPage({ enabled, onUnauthorized }: Options) {
  const [automations, setAutomations] = useState<Automation[]>([])
  const [runs, setRuns] = useState<AutomationRun[]>([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Automation | null>(null)
  const [deleting, setDeleting] = useState<Automation | null>(null)
  const [runningId, setRunningId] = useState<number | null>(null)

  const handleError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError && error.status === 401) return onUnauthorized()
      toast.error(error instanceof Error ? error.message : "Algo salió mal.")
    },
    [onUnauthorized],
  )

  const refresh = useCallback(async () => {
    try {
      const [{ automations: items }, { runs: history }] = await Promise.all([
        api.listAutomations(),
        api.listRuns(RUN_HISTORY_LIMIT),
      ])
      setAutomations(items)
      setRuns(history)
    } catch (error) {
      handleError(error)
    } finally {
      setLoading(false)
    }
  }, [handleError])

  const handleCreate = useCallback(() => {
    setEditing(null)
    setFormOpen(true)
  }, [])

  const handleEdit = useCallback((automation: Automation) => {
    setEditing(automation)
    setFormOpen(true)
  }, [])

  const handleSave = useCallback(
    async (input: AutomationInput) => {
      try {
        if (editing) await api.updateAutomation(editing.id, input)
        else await api.createAutomation(input)
        toast.success(editing ? "Automatización actualizada." : "Automatización creada.")
        setFormOpen(false)
        await refresh()
        return true
      } catch (error) {
        handleError(error)
        return false
      }
    },
    [editing, handleError, refresh],
  )

  const handleDelete = useCallback(async () => {
    if (!deleting) return
    try {
      await api.deleteAutomation(deleting.id)
      toast.success(`Se eliminó «${deleting.name}».`)
      setDeleting(null)
      await refresh()
    } catch (error) {
      handleError(error)
    }
  }, [deleting, handleError, refresh])

  const handleRun = useCallback(
    async (automation: Automation) => {
      setRunningId(automation.id)
      try {
        const run = await api.createRun(automation.id)
        if (run.ok) toast.success(`«${automation.name}» se ejecutó en ${run.duration_ms} ms.`)
        else toast.error(`«${automation.name}» falló: ${run.detail || `código ${run.status_code}`}`)
        await refresh()
      } catch (error) {
        handleError(error)
      } finally {
        setRunningId(null)
      }
    },
    [handleError, refresh],
  )

  useEffect(() => {
    if (enabled) refresh()
  }, [enabled, refresh])

  return {
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
  }
}

import { useState, type FormEvent } from "react"
import { toast } from "sonner"

import { api } from "@/lib/api"
import type { Device } from "@/presentation/types/devices/types"

export function useRenameDevice(device: Device | null, onRenamed: () => void, onClose: () => void) {
  const [name, setName] = useState(device?.name ?? "")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | undefined>()

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!device) return
    const value = name.trim()
    if (!value) return setError("Escribe un nombre.")
    if (value.length > 60) return setError("Máximo 60 caracteres.")
    setSaving(true)
    try {
      await api.renameDevice(device.entity_id, value)
      toast.success(`Ahora se llama «${value}».`)
      onRenamed()
      onClose()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "No se pudo cambiar el nombre.")
    } finally {
      setSaving(false)
    }
  }

  const changeName = (value: string) => {
    setName(value)
    setError(undefined)
  }

  return { name, saving, error, changeName, handleSubmit }
}

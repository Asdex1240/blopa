import { useRef, useState } from "react"
import { toast } from "sonner"

import { api } from "@/lib/api"
import { NEW_DEVICE_POLL_MS, NEW_DEVICE_POLL_TRIES } from "@/presentation/constants/devices/constants"
import type { DeviceSource, NewDeviceName, WizardStep } from "@/presentation/types/devices/types"

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function currentIds() {
  return new Set((await api.listDevices()).devices.map((device) => device.entity_id))
}

export function useAddDeviceWizard(onDevicesChanged: () => void) {
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState<WizardStep>("source")
  const [source, setSource] = useState<DeviceSource | null>(null)
  const [names, setNames] = useState<NewDeviceName[]>([])
  const [looking, setLooking] = useState(false)
  const [saving, setSaving] = useState(false)
  const known = useRef<Set<string>>(new Set())

  const reset = () => {
    setStep("source")
    setSource(null)
    setNames([])
  }

  const handleOpenChange = async (next: boolean) => {
    if (saving || looking) return
    setOpen(next)
    if (!next) {
      reset()
      return
    }
    known.current = await currentIds().catch(() => new Set<string>())
  }

  const handleSelectSource = (selected: DeviceSource) => {
    setSource(selected)
    setStep("connect")
  }

  const handleBack = () => reset()

  const handleConnected = async () => {
    setStep("name")
    setLooking(true)
    onDevicesChanged()
    for (let attempt = 0; attempt < NEW_DEVICE_POLL_TRIES; attempt += 1) {
      const devices = (await api.listDevices().catch(() => ({ devices: [] }))).devices
      const fresh = devices.filter((device) => !known.current.has(device.entity_id))
      if (fresh.length) {
        setNames(fresh.map((device) => ({ entity_id: device.entity_id, original: device.name, name: device.name })))
        break
      }
      await wait(NEW_DEVICE_POLL_MS)
    }
    setLooking(false)
  }

  const setName = (entityId: string, name: string) =>
    setNames((current) => current.map((item) => (item.entity_id === entityId ? { ...item, name } : item)))

  const handleSaveNames = async () => {
    setSaving(true)
    try {
      for (const item of names) {
        if (item.name.trim() && item.name.trim() !== item.original) await api.renameDevice(item.entity_id, item.name.trim())
      }
      toast.success(names.length ? "Listo, ya puedes usarlos por chat." : "Listo.")
      onDevicesChanged()
      setOpen(false)
      reset()
    } catch (reason) {
      toast.error(reason instanceof Error ? reason.message : "No se pudo guardar el nombre.")
    } finally {
      setSaving(false)
    }
  }

  return {
    open,
    step,
    source,
    names,
    looking,
    saving,
    setName,
    handleOpenChange,
    handleSelectSource,
    handleBack,
    handleConnected,
    handleSaveNames,
  }
}

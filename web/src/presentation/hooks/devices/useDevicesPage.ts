import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"

import { api, ApiError } from "@/lib/api"
import { DEVICE_REFRESH_MS } from "@/presentation/constants/devices/constants"
import type { Device, DeviceAction } from "@/presentation/types/devices/types"
import { describeAction } from "@/presentation/utils/devices/describeAction"
import { groupDevices } from "@/presentation/utils/devices/groupDevices"

type Options = { enabled: boolean; onUnauthorized: () => void }

export function useDevicesPage({ enabled, onUnauthorized }: Options) {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [confirming, setConfirming] = useState<DeviceAction | null>(null)
  const [renaming, setRenaming] = useState<Device | null>(null)

  const handleError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError && error.status === 401) return onUnauthorized()
      toast.error(error instanceof Error ? error.message : "Algo salió mal.")
    },
    [onUnauthorized],
  )

  const refresh = useCallback(async () => {
    try {
      setDevices((await api.listDevices()).devices)
    } catch (error) {
      handleError(error)
    } finally {
      setLoading(false)
    }
  }, [handleError])

  const run = useCallback(
    async (request: DeviceAction) => {
      setBusyId(request.device.entity_id)
      try {
        await api.createDeviceAction(request.device.entity_id, request.action, request.value)
        await refresh()
      } catch (error) {
        handleError(error)
      } finally {
        setBusyId(null)
      }
    },
    [handleError, refresh],
  )

  const handleAction = useCallback(
    (request: DeviceAction) => {
      if (request.device.sensitive) return setConfirming(request)
      run(request)
    },
    [run],
  )

  const handleConfirm = useCallback(async () => {
    if (!confirming) return
    const request = confirming
    setConfirming(null)
    await run(request)
    toast.success(describeAction(request))
  }, [confirming, run])

  useEffect(() => {
    if (!enabled) return
    refresh()
    const timer = setInterval(refresh, DEVICE_REFRESH_MS)
    return () => clearInterval(timer)
  }, [enabled, refresh])

  return {
    groups: groupDevices(devices),
    loading,
    busyId,
    confirming,
    setConfirming,
    renaming,
    setRenaming,
    handleAction,
    handleConfirm,
    refresh,
  }
}

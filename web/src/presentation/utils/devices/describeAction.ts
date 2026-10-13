import { ACTION_LABELS } from "@/presentation/constants/devices/constants"
import type { DeviceAction } from "@/presentation/types/devices/types"

export function describeAction({ device, action, value }: DeviceAction) {
  if (action === "ajustar_temperatura") return `Poner «${device.name}» a ${value} °C`
  return `${ACTION_LABELS[action] ?? action}: «${device.name}»`
}

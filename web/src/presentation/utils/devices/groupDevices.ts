import { GROUPS } from "@/presentation/constants/devices/constants"
import type { Device, DeviceGroup } from "@/presentation/types/devices/types"

export function groupDevices(devices: Device[]): DeviceGroup[] {
  return GROUPS.map(({ domain, title }) => ({
    domain,
    title,
    devices: devices.filter((device) => device.domain === domain),
  })).filter((group) => group.devices.length > 0)
}

export type Device = {
  entity_id: string
  name: string
  domain: string
  state: string
  attributes: {
    brightness?: number
    current_temperature?: number
    temperature?: number
    current_position?: number
  }
  kind: string
  state_label: string
  sensitive: boolean
  actions: string[]
}

export type DeviceAction = { device: Device; action: string; value?: number }

export type DeviceGroup = { domain: string; title: string; devices: Device[] }

export type DiscoveredDevice = {
  id: string
  name: string
  vendor_id: number | null
  product_id: number | null
  host: string | null
  addresses: string[]
  commissioning_mode: number | null
}

export type Account = { id: string; provider: "tuya"; title: string; state: string | null }

export type TuyaLink = { id: string; qr: string | null }

export type TuyaConfirmation = { connected: boolean; title: string | null; qr: string | null }

export type DeviceSource = "smartlife" | "generic" | "alexa" | "google" | "matter-code"

export type WizardStep = "source" | "connect" | "name"

export type SourceOption = { id: DeviceSource; title: string; description: string; matter: boolean }

export type NewDeviceName = { entity_id: string; original: string; name: string }

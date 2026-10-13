import { PAIRING_CODE_PATTERN } from "@/presentation/constants/devices/constants"

export const normalizeCode = (code: string) => {
  const trimmed = code.trim()
  return trimmed.toUpperCase().startsWith("MT:") ? trimmed.toUpperCase() : trimmed.replace(/[\s-]/g, "")
}

export function validatePairingCode(code: string) {
  if (PAIRING_CODE_PATTERN.test(normalizeCode(code))) return undefined
  return "Escribe los 11 dígitos del código (con o sin guiones) o el texto del QR que empieza con MT:."
}

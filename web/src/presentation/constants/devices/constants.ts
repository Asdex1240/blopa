import type { SourceOption } from "@/presentation/types/devices/types"
import { DoorClosedIcon, FanIcon, LampIcon, LockIcon, PlugIcon, ThermometerIcon, WorkflowIcon, type LucideIcon } from "lucide-react"

export const DEVICE_REFRESH_MS = 10000

export const GROUPS: { domain: string; title: string }[] = [
  { domain: "light", title: "Luces" },
  { domain: "switch", title: "Enchufes" },
  { domain: "fan", title: "Ventiladores" },
  { domain: "climate", title: "Clima" },
  { domain: "cover", title: "Persianas y puertas" },
  { domain: "lock", title: "Cerraduras" },
  { domain: "script", title: "Scripts" },
  { domain: "automation", title: "Automatizaciones de Home Assistant" },
]

export const DOMAIN_ICONS: Record<string, LucideIcon> = {
  light: LampIcon,
  switch: PlugIcon,
  fan: FanIcon,
  climate: ThermometerIcon,
  cover: DoorClosedIcon,
  lock: LockIcon,
  script: WorkflowIcon,
  automation: WorkflowIcon,
}

export const ACTION_LABELS: Record<string, string> = {
  encender: "Encender",
  apagar: "Apagar",
  bloquear: "Cerrar con llave",
  desbloquear: "Quitar llave",
  abrir: "Abrir",
  cerrar: "Cerrar",
  detener: "Detener",
  ejecutar: "Ejecutar",
  ajustar_temperatura: "Ajustar temperatura",
  ajustar_brillo: "Ajustar brillo",
}

export const TOGGLE_DOMAINS = new Set(["light", "switch", "fan"])

export const TEMPERATURE_STEP = 1

export const DISCOVERY_REFRESH_MS = 5000

export const PAIRING_CODE_PATTERN = /^(MT:[A-Z0-9.-]+|\d{11}|\d{21})$/i

export const SOURCE_OPTIONS: SourceOption[] = [
  { id: "smartlife", title: "Smart Life o Tuya Smart", description: "Focos y enchufes Wi-Fi genéricos que controlas con esas apps.", matter: false },
  { id: "generic", title: "Steren Home u otra app de marca", description: "Apps basadas en Tuya; se pasan a Smart Life en un par de minutos.", matter: false },
  { id: "alexa", title: "Alexa", description: "Dispositivos Matter que ya funcionan con tu Echo.", matter: true },
  { id: "google", title: "Google Home", description: "Dispositivos Matter que ya funcionan con Google.", matter: true },
  { id: "matter-code", title: "Tiene logo Matter y su código", description: "Dispositivo nuevo con el QR o los 11 dígitos impresos.", matter: true },
]

export const GENERIC_APP_STEPS = [
  "Instala Smart Life (app naranja de Tuya Inc.) y crea una cuenta.",
  "En la app de tu marca (por ejemplo Steren Home), elimina el dispositivo. Quedará parpadeando.",
  "En Smart Life toca «+ → Agregar dispositivo». Si aparece «dispositivo encontrado», tócalo; si no, elige su tipo (Iluminación → Foco Wi-Fi).",
  "Comprueba que lo prendes y apagas desde Smart Life.",
]

export const MATTER_SHARE_STEPS: Record<string, string[]> = {
  alexa: [
    "En la app de Alexa abre Dispositivos y toca el dispositivo.",
    "Entra a Configuración (engrane) → «Otros asistentes y aplicaciones» → «Agregar otro».",
    "Copia el código de 11 dígitos y pégalo abajo antes de que caduque.",
  ],
  google: [
    "En Google Home toca el dispositivo y entra a Configuración (engrane).",
    "Abre «Apps y servicios Matter vinculados» → «Vincular apps y servicios».",
    "Copia el código de 11 dígitos y pégalo abajo antes de que caduque.",
  ],
  "matter-code": [
    "Conecta el dispositivo a tu Wi-Fi con la app del fabricante, Alexa o Google Home.",
    "Desde esa app genera un código para compartir y pégalo abajo.",
    "El código impreso en la caja solo sirve para la primera configuración.",
  ],
}

export const NEW_DEVICE_POLL_MS = 2000

export const NEW_DEVICE_POLL_TRIES = 10

export const SMART_LIFE_USER_CODE_PATH = "Yo → Configuración (engrane) → Cuenta y seguridad → Código de usuario"

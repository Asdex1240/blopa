import { WEBHOOK_PATH_PATTERN } from "@/presentation/constants/automations/constants"
import type { AutomationFormErrors, AutomationInput } from "@/presentation/types/automations/types"

export function validateAutomation(input: AutomationInput): AutomationFormErrors {
  const errors: AutomationFormErrors = {}
  if (!input.name.trim()) errors.name = "Escribe un nombre."
  else if (input.name.trim().length > 60) errors.name = "Máximo 60 caracteres."
  if (!input.description.trim()) errors.description = "Describe qué hace; BLOPA la usa para decidir cuándo lanzarla."
  else if (input.description.trim().length > 300) errors.description = "Máximo 300 caracteres."
  if (!WEBHOOK_PATH_PATTERN.test(input.webhook_path.trim())) errors.webhook_path = "Solo letras, números, guiones y diagonales. Ejemplo: blopa-ping"
  return errors
}

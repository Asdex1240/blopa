import { useState, type FormEvent } from "react"

import { EMPTY_AUTOMATION } from "@/presentation/constants/automations/constants"
import type { Automation, AutomationFormErrors, AutomationInput } from "@/presentation/types/automations/types"
import { validateAutomation } from "@/presentation/utils/automations/validateAutomation"

const toInput = (automation: Automation | null): AutomationInput =>
  automation
    ? {
        name: automation.name,
        description: automation.description,
        webhook_path: automation.webhook_path,
        requires_confirmation: automation.requires_confirmation,
      }
    : EMPTY_AUTOMATION

export function useAutomationForm(automation: Automation | null, onSave: (input: AutomationInput) => Promise<boolean>) {
  const [values, setValues] = useState<AutomationInput>(() => toInput(automation))
  const [errors, setErrors] = useState<AutomationFormErrors>({})
  const [saving, setSaving] = useState(false)

  const setField = <K extends keyof AutomationInput>(field: K, value: AutomationInput[K]) => {
    setValues((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const input = {
      ...values,
      name: values.name.trim(),
      description: values.description.trim(),
      webhook_path: values.webhook_path.trim(),
    }
    const found = validateAutomation(input)
    setErrors(found)
    if (Object.keys(found).length) return
    setSaving(true)
    await onSave(input)
    setSaving(false)
  }

  return { values, errors, saving, setField, handleSubmit }
}

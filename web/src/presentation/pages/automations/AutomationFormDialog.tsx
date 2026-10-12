import type { Automation, AutomationInput } from "@/presentation/types/automations/types"
import { AutomationForm } from "./AutomationForm"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"

type Props = {
  open: boolean
  automation: Automation | null
  onOpenChange: (open: boolean) => void
  onSave: (input: AutomationInput) => Promise<boolean>
}

export function AutomationFormDialog({ open, automation, onOpenChange, onSave }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{automation ? "Editar automatización" : "Nueva automatización"}</DialogTitle>
          <DialogDescription>El flujo de n8n debe empezar con un nodo Webhook de tipo POST y estar publicado.</DialogDescription>
        </DialogHeader>
        {open && <AutomationForm key={automation?.id ?? "new"} automation={automation} onCancel={() => onOpenChange(false)} onSave={onSave} />}
      </DialogContent>
    </Dialog>
  )
}

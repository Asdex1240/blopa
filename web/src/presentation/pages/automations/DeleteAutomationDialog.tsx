import type { Automation } from "@/presentation/types/automations/types"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

type Props = {
  automation: Automation | null
  onCancel: () => void
  onConfirm: () => void
}

export function DeleteAutomationDialog({ automation, onCancel, onConfirm }: Props) {
  return (
    <AlertDialog open={automation !== null} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>¿Eliminar «{automation?.name}»?</AlertDialogTitle>
          <AlertDialogDescription>
            BLOPA dejará de poder lanzarla y se borrará su historial. El flujo en n8n no se toca.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction variant="destructive" onClick={onConfirm}>
            Eliminar
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

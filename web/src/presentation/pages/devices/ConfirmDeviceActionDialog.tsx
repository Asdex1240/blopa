import type { DeviceAction } from "@/presentation/types/devices/types"
import { describeAction } from "@/presentation/utils/devices/describeAction"
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

type Props = { request: DeviceAction | null; onCancel: () => void; onConfirm: () => void }

export function ConfirmDeviceActionDialog({ request, onCancel, onConfirm }: Props) {
  return (
    <AlertDialog open={request !== null} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{request ? describeAction(request) : ""}</AlertDialogTitle>
          <AlertDialogDescription>
            {request?.device.kind === "cerradura"
              ? "Es una cerradura: confirma que quieres cambiarla."
              : "Este dispositivo pide confirmación antes de actuar."}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>No</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>Sí, hazlo</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

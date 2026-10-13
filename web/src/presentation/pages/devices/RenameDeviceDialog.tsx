import { Loader2Icon } from "lucide-react"

import { useRenameDevice } from "@/presentation/hooks/devices/useRenameDevice"
import { FieldError } from "@/presentation/pages/shared/FieldError"
import type { Device } from "@/presentation/types/devices/types"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type FormProps = { device: Device; onRenamed: () => void; onClose: () => void }

function RenameForm({ device, onRenamed, onClose }: FormProps) {
  const { name, saving, error, changeName, handleSubmit } = useRenameDevice(device, onRenamed, onClose)
  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="space-y-1.5">
        <Label htmlFor="device-name" className="text-xs font-medium">
          Nombre
        </Label>
        <Input
          id="device-name"
          value={name}
          onChange={(event) => changeName(event.target.value)}
          autoFocus
          aria-invalid={Boolean(error)}
          className="h-9 bg-background"
        />
        <FieldError message={error} />
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button type="submit" disabled={saving}>
          {saving && <Loader2Icon className="animate-spin" />}
          Guardar
        </Button>
      </DialogFooter>
    </form>
  )
}

type Props = { device: Device | null; onRenamed: () => void; onClose: () => void }

export function RenameDeviceDialog({ device, onRenamed, onClose }: Props) {
  return (
    <Dialog open={device !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Cambiar nombre</DialogTitle>
          <DialogDescription>Usa el nombre con el que se lo pedirías a BLOPA, por ejemplo «luz del cuarto».</DialogDescription>
        </DialogHeader>
        {device && <RenameForm key={device.entity_id} device={device} onRenamed={onRenamed} onClose={onClose} />}
      </DialogContent>
    </Dialog>
  )
}

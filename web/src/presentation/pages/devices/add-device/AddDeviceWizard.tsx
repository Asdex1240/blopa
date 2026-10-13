import { ArrowLeftIcon, PlusIcon } from "lucide-react"

import { MATTER_SHARE_STEPS, SOURCE_OPTIONS } from "@/presentation/constants/devices/constants"
import { useAddDeviceWizard } from "@/presentation/hooks/devices/useAddDeviceWizard"
import { SourceStep } from "./Components"
import { MatterStep } from "./MatterStep"
import { NameDevicesStep } from "./NameDevicesStep"
import { TuyaStep } from "./TuyaStep"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

type Props = { matterEnabled: boolean; onDevicesChanged: () => void }

const TITLES = { source: "Agregar dispositivo", connect: "Conectar", name: "Ponle nombre" }

export function AddDeviceWizard({ matterEnabled, onDevicesChanged }: Props) {
  const {
    open,
    step,
    source,
    names,
    looking,
    saving,
    setName,
    handleOpenChange,
    handleSelectSource,
    handleBack,
    handleConnected,
    handleSaveNames,
  } = useAddDeviceWizard(onDevicesChanged)
  const option = SOURCE_OPTIONS.find((item) => item.id === source)

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <PlusIcon />
          Agregar
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90dvh] overflow-y-auto sm:max-w-lg" showCloseButton={!saving && !looking}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {step === "connect" && (
              <Button variant="ghost" size="icon-sm" onClick={handleBack} aria-label="Regresar">
                <ArrowLeftIcon />
              </Button>
            )}
            {step === "connect" && option ? option.title : TITLES[step]}
          </DialogTitle>
          <DialogDescription>
            {step === "name" ? "Así lo vas a pedir en el chat." : "Te guiamos según la app con la que ya lo usas."}
          </DialogDescription>
        </DialogHeader>
        {step === "source" && <SourceStep matterEnabled={matterEnabled} onSelect={handleSelectSource} />}
        {step === "connect" && (source === "smartlife" || source === "generic") && (
          <TuyaStep moveFirst={source === "generic"} onConnected={handleConnected} />
        )}
        {step === "connect" && source && MATTER_SHARE_STEPS[source] && (
          <MatterStep steps={MATTER_SHARE_STEPS[source]} onPaired={handleConnected} />
        )}
        {step === "name" && (
          <NameDevicesStep names={names} looking={looking} saving={saving} onNameChange={setName} onSave={handleSaveNames} />
        )}
      </DialogContent>
    </Dialog>
  )
}

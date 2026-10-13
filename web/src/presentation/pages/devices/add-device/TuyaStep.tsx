import { CircleAlertIcon, CircleCheckIcon, Loader2Icon, RefreshCwIcon, ScanLineIcon } from "lucide-react"

import { GENERIC_APP_STEPS, SMART_LIFE_USER_CODE_PATH } from "@/presentation/constants/devices/constants"
import { useTuyaLink } from "@/presentation/hooks/devices/useTuyaLink"
import { SectionTitle } from "@/presentation/pages/shared/SectionTitle"
import { StepList } from "./Components"
import { QrCode } from "./QrCode"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Props = { moveFirst: boolean; onConnected: () => void }

function Failure({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <p className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
      <CircleAlertIcon className="mt-0.5 size-3.5 shrink-0" />
      {message}
    </p>
  )
}

export function TuyaStep({ moveFirst, onConnected }: Props) {
  const { accounts, userCode, link, busy, error, notYet, setUserCode, handleStart, handleConfirm, handleRefresh } =
    useTuyaLink(onConnected)

  if (accounts === null) {
    return <Loader2Icon className="mx-auto my-6 size-5 animate-spin text-muted-foreground" />
  }

  if (accounts.length > 0 && !link) {
    return (
      <div className="grid gap-4">
        <div className="flex items-start gap-3 rounded-lg border p-3">
          <CircleCheckIcon className="mt-0.5 size-4 shrink-0 text-success" />
          <div className="text-sm">
            <p className="font-medium">Tu cuenta Smart Life ya está conectada</p>
            <p className="text-xs text-muted-foreground">
              {moveFirst ? "Pasa el dispositivo a Smart Life con los pasos de abajo y después búscalo aquí." : "Agrega el dispositivo en Smart Life y después búscalo aquí."}
            </p>
          </div>
        </div>
        {moveFirst && <StepList steps={GENERIC_APP_STEPS} />}
        <Failure message={error} />
        <Button onClick={handleRefresh} disabled={busy}>
          {busy ? <Loader2Icon className="animate-spin" /> : <RefreshCwIcon />}
          Buscar dispositivos nuevos
        </Button>
      </div>
    )
  }

  if (link) {
    return (
      <div className="grid gap-4">
        <StepList
          steps={[
            "Abre Smart Life en tu celular y toca el escáner (arriba a la derecha).",
            "Escanea este código y confirma el inicio de sesión.",
            "Regresa aquí y presiona «Ya lo escaneé».",
          ]}
        />
        <QrCode data={link.qr} />
        {notYet && (
          <p className="text-center text-xs text-warning">
            Smart Life aún no lo confirmaba, así que se generó un código nuevo. Escanéalo y vuelve a intentar.
          </p>
        )}
        <Failure message={error} />
        <Button onClick={handleConfirm} disabled={busy}>
          {busy ? <Loader2Icon className="animate-spin" /> : <ScanLineIcon />}
          Ya lo escaneé
        </Button>
      </div>
    )
  }

  return (
    <form onSubmit={handleStart} className="grid gap-4">
      {moveFirst && (
        <div>
          <SectionTitle>Primero, pásalo a Smart Life</SectionTitle>
          <StepList steps={GENERIC_APP_STEPS} />
        </div>
      )}
      <div className="space-y-1.5">
        <Label htmlFor="tuya-user-code" className="text-xs font-medium">
          Código de usuario de Smart Life
        </Label>
        <Input
          id="tuya-user-code"
          value={userCode}
          onChange={(event) => setUserCode(event.target.value)}
          placeholder="BaJ0orh"
          autoComplete="off"
          className="h-9 bg-background font-mono"
        />
        <p className="text-xs text-muted-foreground">En Smart Life: {SMART_LIFE_USER_CODE_PATH}.</p>
      </div>
      <Failure message={error} />
      <Button type="submit" disabled={busy}>
        {busy && <Loader2Icon className="animate-spin" />}
        Continuar
      </Button>
    </form>
  )
}

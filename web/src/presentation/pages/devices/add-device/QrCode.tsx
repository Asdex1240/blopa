import { Loader2Icon } from "lucide-react"

import { useQrImage } from "@/presentation/hooks/devices/useQrImage"

export function QrCode({ data }: { data: string | null }) {
  const image = useQrImage(data)
  return (
    <div className="mx-auto flex size-56 items-center justify-center rounded-xl bg-white p-2">
      {image ? (
        <img src={image} alt="Código QR para iniciar sesión en Smart Life" className="size-full" />
      ) : (
        <Loader2Icon className="size-6 animate-spin text-neutral-400" />
      )}
    </div>
  )
}

import { useEffect, useState } from "react"
import QRCode from "qrcode"

export function useQrImage(data: string | null) {
  const [image, setImage] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    if (!data) return
    QRCode.toDataURL(data, { errorCorrectionLevel: "Q", margin: 2, scale: 6 })
      .then((url) => active && setImage(url))
      .catch(() => active && setImage(null))
    return () => {
      active = false
    }
  }, [data])

  return data ? image : null
}

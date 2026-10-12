import { useState, type FormEvent } from "react"
import { toast } from "sonner"

import { TOKEN_KEY } from "@/lib/api"
import { storage } from "@/lib/storage"

export function useSettingsPage(onTokenSaved: () => void) {
  const [token, setToken] = useState(() => storage.get(TOKEN_KEY))

  const handleSaveToken = (event: FormEvent) => {
    event.preventDefault()
    storage.set(TOKEN_KEY, token.trim())
    toast.success("Token guardado.")
    onTokenSaved()
  }

  return { token, setToken, handleSaveToken }
}

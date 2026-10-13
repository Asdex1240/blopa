import { useCallback, useEffect, useState, type FormEvent } from "react"

import { api } from "@/lib/api"
import { DISCOVERY_REFRESH_MS } from "@/presentation/constants/devices/constants"
import type { DiscoveredDevice } from "@/presentation/types/devices/types"
import { normalizeCode, validatePairingCode } from "@/presentation/utils/devices/validatePairing"

export function useMatterPairing(onPaired: () => void) {
  const [code, setCodeValue] = useState("")
  const [error, setError] = useState<string | undefined>()
  const [discovered, setDiscovered] = useState<DiscoveredDevice[]>([])
  const [searching, setSearching] = useState(false)
  const [pairing, setPairing] = useState(false)
  const [failure, setFailure] = useState<string | null>(null)

  const setCode = (value: string) => {
    setCodeValue(value)
    setError(undefined)
  }

  const search = useCallback(async () => {
    setSearching(true)
    try {
      setDiscovered((await api.listDiscovered()).devices)
    } catch {
      setDiscovered([])
    } finally {
      setSearching(false)
    }
  }, [])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const problem = validatePairingCode(code)
    setError(problem)
    if (problem) return
    setPairing(true)
    setFailure(null)
    try {
      await api.createPairing(normalizeCode(code))
      onPaired()
    } catch (reason) {
      setFailure(reason instanceof Error ? reason.message : "No se pudo emparejar.")
    } finally {
      setPairing(false)
    }
  }

  useEffect(() => {
    search()
    const timer = setInterval(search, DISCOVERY_REFRESH_MS)
    return () => clearInterval(timer)
  }, [search])

  return { code, error, discovered, searching, pairing, failure, setCode, handleSubmit }
}

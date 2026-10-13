import { useCallback, useEffect, useRef, useState, type FormEvent } from "react"

import { api } from "@/lib/api"
import type { Account, TuyaLink } from "@/presentation/types/devices/types"

export function useTuyaLink(onConnected: () => void) {
  const [accounts, setAccounts] = useState<Account[] | null>(null)
  const [userCode, setUserCode] = useState("")
  const [link, setLink] = useState<TuyaLink | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notYet, setNotYet] = useState(false)
  const pending = useRef<string | null>(null)

  const fail = (reason: unknown) => setError(reason instanceof Error ? reason.message : "Algo salió mal.")

  const handleStart = async (event: FormEvent) => {
    event.preventDefault()
    if (!userCode.trim()) return setError("Pega tu código de usuario de Smart Life.")
    setBusy(true)
    setError(null)
    try {
      const created = await api.createTuyaLink(userCode.trim())
      pending.current = created.id
      setLink(created)
    } catch (reason) {
      fail(reason)
    } finally {
      setBusy(false)
    }
  }

  const handleConfirm = async () => {
    if (!link) return
    setBusy(true)
    setError(null)
    try {
      const result = await api.confirmTuyaLink(link.id)
      if (result.connected) {
        pending.current = null
        onConnected()
        return
      }
      setNotYet(true)
      setLink({ id: link.id, qr: result.qr })
    } catch (reason) {
      fail(reason)
    } finally {
      setBusy(false)
    }
  }

  const handleRefresh = async () => {
    setBusy(true)
    setError(null)
    try {
      await api.refreshTuya()
      onConnected()
    } catch (reason) {
      fail(reason)
    } finally {
      setBusy(false)
    }
  }

  const loadAccounts = useCallback(async () => {
    try {
      setAccounts((await api.listAccounts()).accounts)
    } catch {
      setAccounts([])
    }
  }, [])

  useEffect(() => {
    loadAccounts()
    return () => {
      if (pending.current) api.cancelTuyaLink(pending.current).catch(() => undefined)
    }
  }, [loadAccounts])

  return { accounts, userCode, link, busy, error, notYet, setUserCode, handleStart, handleConfirm, handleRefresh }
}

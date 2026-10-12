import { useCallback, useEffect, useState } from "react"

import { api } from "@/lib/api"
import { HEALTH_REFRESH_MS } from "@/presentation/constants/layout/constants"
import type { Health } from "@/presentation/types/api/types"

export function useHealth() {
  const [health, setHealth] = useState<Health | null>(null)
  const [online, setOnline] = useState(true)

  const refresh = useCallback(async () => {
    try {
      setHealth(await api.health())
      setOnline(true)
    } catch {
      setOnline(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, HEALTH_REFRESH_MS)
    return () => clearInterval(timer)
  }, [refresh])

  return { health, online, refresh }
}

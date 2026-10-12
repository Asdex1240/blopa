import { useEffect, useState } from "react"

import type { Theme } from "@/presentation/types/layout/types"

const darkQuery = () => window.matchMedia("(prefers-color-scheme: dark)")

const currentTheme = (): Theme => (darkQuery().matches ? "dark" : "light")

export function useSystemTheme() {
  const [theme, setTheme] = useState<Theme>(currentTheme)

  useEffect(() => {
    const media = darkQuery()
    const update = () => setTheme(currentTheme())
    media.addEventListener("change", update)
    return () => media.removeEventListener("change", update)
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
  }, [theme])

  return theme
}

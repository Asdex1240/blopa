import type { ReactNode } from "react"

export function SectionTitle({ children }: { children: ReactNode }) {
  return <p className="mb-4 text-xs font-semibold tracking-wide text-muted-foreground uppercase">{children}</p>
}

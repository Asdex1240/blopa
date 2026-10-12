import type { ReactNode } from "react"

export function SectionTitle({ children }: { children: ReactNode }) {
  return <p className="mb-4 text-xs font-semibold tracking-wide text-muted-foreground uppercase">{children}</p>
}

export function SettingRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <>
      <dt className="text-muted-foreground">{label}</dt>
      <dd>{children}</dd>
    </>
  )
}

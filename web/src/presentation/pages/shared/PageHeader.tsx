import type { ReactNode } from "react"

export function PageHeader({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="app-drag -mx-4 flex h-14 shrink-0 items-center justify-between gap-4 border-b px-4">
      <h1 className="text-base font-semibold">{title}</h1>
      <div className="app-no-drag flex items-center gap-2">{children}</div>
    </header>
  )
}

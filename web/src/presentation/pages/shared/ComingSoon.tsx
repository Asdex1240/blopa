import type { LucideIcon } from "lucide-react"

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

type Props = { icon: LucideIcon; description: string; phase: number }

export function ComingSoon({ icon: Icon, description, phase }: Props) {
  return (
    <Card>
      <CardHeader>
        <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-muted">
          <Icon className="size-5 text-muted-foreground" />
        </div>
        <CardTitle>{description}</CardTitle>
        <CardDescription>Disponible en la fase {phase}.</CardDescription>
      </CardHeader>
    </Card>
  )
}

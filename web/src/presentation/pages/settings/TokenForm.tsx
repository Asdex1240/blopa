import type { FormEvent } from "react"

import { SectionTitle } from "./Components"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Props = {
  token: string
  onTokenChange: (token: string) => void
  onSubmit: (event: FormEvent) => void
}

export function TokenForm({ token, onTokenChange, onSubmit }: Props) {
  return (
    <Card>
      <CardContent>
        <SectionTitle>Token de acceso</SectionTitle>
        <form onSubmit={onSubmit} className="grid gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="token" className="text-xs font-medium">
              Token
            </Label>
            <Input
              id="token"
              type="password"
              autoComplete="current-password"
              value={token}
              onChange={(event) => onTokenChange(event.target.value)}
              placeholder="Solo si el servidor tiene BLOPA_API_TOKEN"
              className="h-9 bg-background"
            />
          </div>
          <Button type="submit" className="h-9 justify-self-start">
            Guardar
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

import { useSettingsPage } from "@/presentation/hooks/settings/useSettingsPage"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"
import { SystemDetails } from "@/presentation/pages/settings/SystemDetails"
import { TokenForm } from "@/presentation/pages/settings/TokenForm"
import { VoiceSettings } from "@/presentation/pages/settings/VoiceSettings"
import type { Health } from "@/presentation/types/api/types"

type Props = {
  health: Health | null
  speakAll: boolean
  onSpeakAllChange: (value: boolean) => void
  onTestVoice: () => void
  onTokenSaved: () => void
}

export default function SettingsPage({ health, speakAll, onSpeakAllChange, onTestVoice, onTokenSaved }: Props) {
  const { token, setToken, handleSaveToken } = useSettingsPage(onTokenSaved)

  return (
    <div className="flex flex-col gap-4 pb-6">
      <PageHeader title="Ajustes" />
      <SystemDetails health={health} />
      <VoiceSettings health={health} speakAll={speakAll} onSpeakAllChange={onSpeakAllChange} onTestVoice={onTestVoice} />
      <TokenForm token={token} onTokenChange={setToken} onSubmit={handleSaveToken} />
    </div>
  )
}

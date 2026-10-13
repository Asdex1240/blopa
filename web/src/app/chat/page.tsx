import { RotateCcwIcon } from "lucide-react"

import { useChatPage } from "@/presentation/hooks/chat/useChatPage"
import { ChatComposer } from "@/presentation/pages/chat/ChatComposer"
import { MessageList } from "@/presentation/pages/chat/MessageList"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"
import { Button } from "@/components/ui/button"

type Props = {
  authVersion: number
  voiceEnabled: boolean
  speakAll: boolean
  onSpeak: (text: string) => void
  onUnauthorized: () => void
  onReplied: () => void
}

export default function ChatPage({ authVersion, voiceEnabled, speakAll, onSpeak, onUnauthorized, onReplied }: Props) {
  const { messages, busy, confirmation, endRef, handleSend, handleVoiceText, handleReset, handleConfirm, handleCancel } =
    useChatPage({ authVersion, speakAll, onSpeak, onUnauthorized, onReplied })

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 pb-6">
      <PageHeader title="Chat">
        <Button variant="outline" onClick={handleReset} disabled={busy}>
          <RotateCcwIcon />
          Nueva conversación
        </Button>
      </PageHeader>
      <MessageList
        messages={messages}
        busy={busy}
        confirmation={confirmation}
        endRef={endRef}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
      <ChatComposer busy={busy} voiceEnabled={voiceEnabled} onSend={handleSend} onVoiceText={handleVoiceText} />
    </div>
  )
}

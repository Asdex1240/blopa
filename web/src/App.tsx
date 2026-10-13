import AutomationsPage from "@/app/automations/page"
import ChatPage from "@/app/chat/page"
import DevicesPage from "@/app/devices/page"
import SettingsPage from "@/app/settings/page"
import { cn } from "@/lib/utils"
import { useAppShell } from "@/presentation/hooks/layout/useAppShell"
import { AppSidebar } from "@/presentation/pages/layout/AppSidebar"
import { MobileHeader } from "@/presentation/pages/layout/MobileHeader"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"

export default function App() {
  const { view, setView, health, online, refresh, authVersion, speech, voiceReady, handleUnauthorized, handleTokenSaved } =
    useAppShell()

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex h-dvh flex-col md:flex-row">
        <AppSidebar view={view} onSelect={setView} health={health} online={online} />
        <MobileHeader view={view} onSelect={setView} health={health} online={online} />
        <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-y-auto px-4">
          <section className={cn("min-h-0 flex-1 flex-col", view === "chat" ? "flex" : "hidden")}>
            <ChatPage
              authVersion={authVersion}
              voiceEnabled={voiceReady}
              speakAll={speech.speakAll}
              onSpeak={speech.speak}
              onUnauthorized={handleUnauthorized}
              onReplied={refresh}
            />
          </section>
          {view === "devices" && (
            <DevicesPage
              homeConfigured={health?.services.home_assistant.configured ?? false}
              matterConfigured={health?.services.matter.configured ?? false}
              onUnauthorized={handleUnauthorized}
            />
          )}
          {view === "automations" && (
            <AutomationsPage n8nConfigured={health?.services.n8n.configured ?? false} onUnauthorized={handleUnauthorized} />
          )}
          {view === "settings" && (
            <SettingsPage
              health={health}
              speakAll={speech.speakAll}
              onSpeakAllChange={speech.setSpeakAll}
              onTestVoice={() => speech.speak("Hola, soy BLOPA. Así sueno cuando te respondo.")}
              onTokenSaved={handleTokenSaved}
            />
          )}
        </main>
      </div>
      <Toaster position="top-center" />
    </TooltipProvider>
  )
}

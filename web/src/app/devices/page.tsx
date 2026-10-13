import { useDevicesPage } from "@/presentation/hooks/devices/useDevicesPage"
import { AddDeviceWizard } from "@/presentation/pages/devices/add-device/AddDeviceWizard"
import { ConfirmDeviceActionDialog } from "@/presentation/pages/devices/ConfirmDeviceActionDialog"
import { DeviceGroup, EmptyDevices, HomeAssistantUnavailable } from "@/presentation/pages/devices/Components"
import { RenameDeviceDialog } from "@/presentation/pages/devices/RenameDeviceDialog"
import { PageHeader } from "@/presentation/pages/shared/PageHeader"

type Props = { homeConfigured: boolean; matterConfigured: boolean; onUnauthorized: () => void }

export default function DevicesPage({ homeConfigured, matterConfigured, onUnauthorized }: Props) {
  const { groups, loading, busyId, confirming, setConfirming, renaming, setRenaming, handleAction, handleConfirm, refresh } =
    useDevicesPage({ enabled: homeConfigured, onUnauthorized })

  if (!homeConfigured) {
    return (
      <div className="flex flex-col gap-4 pb-6">
        <PageHeader title="Dispositivos" />
        <HomeAssistantUnavailable />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 pb-6">
      <PageHeader title="Dispositivos">
        <AddDeviceWizard matterEnabled={matterConfigured} onDevicesChanged={refresh} />
      </PageHeader>
      {!loading && groups.length === 0 && <EmptyDevices />}
      {groups.map((group) => (
        <DeviceGroup key={group.domain} group={group} busyId={busyId} onAction={handleAction} onRename={setRenaming} />
      ))}
      <ConfirmDeviceActionDialog request={confirming} onCancel={() => setConfirming(null)} onConfirm={handleConfirm} />
      <RenameDeviceDialog device={renaming} onRenamed={refresh} onClose={() => setRenaming(null)} />
    </div>
  )
}

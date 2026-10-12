type DesktopBridge = { isDesktop: boolean }

export const isDesktop = Boolean((window as Window & { blopa?: DesktopBridge }).blopa?.isDesktop)

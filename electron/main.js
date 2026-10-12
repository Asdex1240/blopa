const { app, BrowserWindow, dialog, session, shell, systemPreferences } = require("electron");
const path = require("node:path");

const SERVER_URL = process.env.BLOPA_URL || "http://localhost:8000";
const SERVER_ORIGIN = new URL(SERVER_URL).origin;
const ALLOWED_PERMISSIONS = new Set(["media"]);

function isServerUrl(url) {
  try {
    return new URL(url).origin === SERVER_ORIGIN;
  } catch {
    return false;
  }
}

function allowOnlyMicrophone() {
  session.defaultSession.setPermissionRequestHandler((contents, permission, callback, details) => {
    const audioOnly = !details.mediaTypes || details.mediaTypes.every((type) => type === "audio");
    callback(ALLOWED_PERMISSIONS.has(permission) && audioOnly && isServerUrl(details.requestingUrl));
  });
  session.defaultSession.setPermissionCheckHandler((contents, permission, origin) => {
    return ALLOWED_PERMISSIONS.has(permission) && isServerUrl(origin);
  });
}

async function askForMicrophone() {
  if (process.platform !== "darwin") return;
  if (systemPreferences.getMediaAccessStatus("microphone") === "granted") return;
  await systemPreferences.askForMediaAccess("microphone");
}

function createWindow() {
  const window = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 420,
    minHeight: 520,
    title: "BLOPA",
    titleBarStyle: "hiddenInset",
    backgroundColor: "#0f1115",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  window.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("https://") || url.startsWith("http://")) shell.openExternal(url);
    return { action: "deny" };
  });

  window.webContents.on("will-navigate", (event, url) => {
    if (isServerUrl(url)) return;
    event.preventDefault();
    shell.openExternal(url);
  });

  window.webContents.on("did-fail-load", async (event, code, description, url, isMainFrame) => {
    if (!isMainFrame) return;
    const { response } = await dialog.showMessageBox(window, {
      type: "warning",
      message: "No puedo conectar con BLOPA",
      detail: `${SERVER_URL} no responde. Revisa que esté arriba con: docker compose up -d`,
      buttons: ["Reintentar", "Salir"],
    });
    if (response === 0) window.loadURL(SERVER_URL);
    else app.quit();
  });

  window.loadURL(SERVER_URL);
}

app.whenReady().then(async () => {
  allowOnlyMicrophone();
  await askForMicrophone();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

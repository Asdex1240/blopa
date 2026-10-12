const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("blopa", { isDesktop: true });

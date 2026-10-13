#!/bin/sh
set -e

LABEL="com.blopa.matter-server"
SOURCE="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Library/Application Support/BLOPA/matter"
TARGET="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

stop() {
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
}

case "$1" in
  install)
    stop
    mkdir -p "$APP_DIR" "$HOME/Library/LaunchAgents"
    cp "$SOURCE/package.json" "$SOURCE/package-lock.json" "$APP_DIR/"
    (cd "$APP_DIR" && npm ci --omit=dev --no-audit --no-fund --silent)
    if [ -d "$SOURCE/data" ] && [ ! -d "$APP_DIR/data" ]; then
      cp -R "$SOURCE/data" "$APP_DIR/data"
    fi
    mkdir -p "$APP_DIR/data"
    sed -e "s#__NODE__#$(command -v node)#" -e "s#__DIR__#$APP_DIR#g" "$SOURCE/$LABEL.plist" > "$TARGET"
    launchctl bootstrap "$DOMAIN" "$TARGET"
    echo "Servidor Matter instalado en $APP_DIR; arranca al iniciar sesión."
    ;;
  uninstall)
    stop
    rm -f "$TARGET"
    echo "Servidor Matter desinstalado. Sus datos siguen en $APP_DIR/data."
    ;;
  status)
    launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -E "^\s+state =|pid =|last exit" || echo "No está instalado."
    ;;
  logs)
    tail -n 40 "$APP_DIR/data/stdout.log"
    ;;
  *)
    echo "Uso: $0 install | uninstall | status | logs"
    exit 1
    ;;
esac

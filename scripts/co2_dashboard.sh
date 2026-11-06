#!/bin/sh
# Dashboard only: this script never opens or restarts the Arduino serial capture.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNIT=incubadora-co2-dashboard
case "${1:-start}" in
  install)
    UNIT_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user
    mkdir -p "$UNIT_DIR"
    systemctl --user stop "$UNIT.service" 2>/dev/null || true
    cat > "$UNIT_DIR/$UNIT.service" <<EOF
[Unit]
Description=Painel local da incubadora CO2
[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=/usr/bin/python3 "$ROOT/scripts/co2_dashboard.py"
Restart=on-failure
RestartSec=2
[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$UNIT.service"
    printf '%s\n' 'http://127.0.0.1:8082'
    ;;
  start)
    if systemctl --user cat "$UNIT.service" >/dev/null 2>&1; then
      systemctl --user restart "$UNIT.service"
    else
      systemd-run --user --unit="$UNIT" --property=Restart=on-failure \
        --working-directory="$ROOT" /usr/bin/python3 "$ROOT/scripts/co2_dashboard.py"
    fi
    printf '%s\n' 'http://127.0.0.1:8082'
    ;;
  stop) systemctl --user stop "$UNIT.service" ;;
  status) systemctl --user status "$UNIT.service" --no-pager ;;
  logs) journalctl --user -u "$UNIT.service" -n 60 --no-pager ;;
  *) printf '%s\n' "Uso: $0 {install|start|stop|status|logs}" >&2; exit 2 ;;
esac

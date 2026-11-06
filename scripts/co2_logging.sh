#!/bin/sh
# Install/manage the USB recorder. No command is sent to the incubator.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNIT=incubadora-co2-logger.service
case "${1:-status}" in
  install)
    DEVICE=${ARDUINO_PORT:-/dev/ttyACM0}
    for candidate in /dev/serial/by-id/*; do
      [ -e "$candidate" ] || continue
      if [ "$(readlink -f "$candidate")" = "$(readlink -f "$DEVICE")" ]; then DEVICE=$candidate; break; fi
    done
    UNIT_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user
    mkdir -p "$UNIT_DIR"
    cat > "$UNIT_DIR/$UNIT" <<EOF
[Unit]
Description=Histórico USB da incubadora CO2
[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=/usr/bin/python3 -u "$ROOT/scripts/co2_logger.py" --port "$DEVICE"
Restart=on-failure
RestartSec=2
TimeoutStopSec=5
[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$UNIT"
    ;;
  start|stop|restart) systemctl --user "$1" "$UNIT" ;;
  status) systemctl --user status "$UNIT" --no-pager ;;
  logs) journalctl --user -u "$UNIT" -n 40 --no-pager ;;
  *) printf '%s\n' "Uso: $0 {install|start|stop|restart|status|logs}" >&2; exit 2 ;;
esac

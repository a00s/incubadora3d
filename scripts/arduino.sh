#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CLI=${ARDUINO_CLI:-arduino-cli}
FQBN=${ARDUINO_FQBN:-arduino:avr:uno}
PORT=${ARDUINO_PORT:-/dev/ttyACM0}
SKETCH="$ROOT/firmware/incubadora"
LIBRARIES="$ROOT/arduino-libraries"
BUILD="$ROOT/.arduino-build"

if ! command -v "$CLI" >/dev/null 2>&1; then
  if [ -x "$HOME/.local/bin/arduino-cli" ]; then
    CLI="$HOME/.local/bin/arduino-cli"
  else
    echo "Arduino CLI não encontrado. Instale-o conforme a seção Arduino do README." >&2
    exit 127
  fi
fi

ACTION=${1:-}
case "$ACTION" in
  setup)
    "$CLI" core update-index
    "$CLI" core install arduino:avr@1.8.8
    "$CLI" lib install 'Ucglib@1.5.2' 'DHT sensor library@1.4.7' 'Adafruit Unified Sensor@1.1.15'
    ;;
  compile)
    "$CLI" compile --fqbn "$FQBN" --libraries "$LIBRARIES" --build-path "$BUILD" "$SKETCH"
    ;;
  upload)
    "$CLI" compile --fqbn "$FQBN" --libraries "$LIBRARIES" --build-path "$BUILD" \
      --upload --verify --port "$PORT" "$SKETCH"
    ;;
  monitor)
    "$CLI" monitor --port "$PORT" --config 9600
    ;;
  *)
    echo "Uso: $0 {setup|compile|upload|monitor}" >&2
    echo "Defina ARDUINO_PORT se a placa não estiver em $PORT." >&2
    exit 2
    ;;
esac

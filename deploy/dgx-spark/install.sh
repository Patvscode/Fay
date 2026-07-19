#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG_DIR="${FAY_CONFIG_DIR:-$HOME/.config/fay}"
DATA_DIR="${FAY_DATA_DIR:-$HOME/.local/share/fay/mcp}"
UNIT_DIR="$HOME/.config/systemd/user"
SPARK_STUDIO_ROOT="${SPARK_STUDIO_ROOT:-$HOME/Workspace/01_Projects/Active/spark-studio}"
TAILNET_IP="$(tailscale ip -4 2>/dev/null | head -n 1 || true)"
if [[ -z "$TAILNET_IP" ]]; then
  TAILNET_IP="127.0.0.1"
fi

python3 -m venv --system-site-packages "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --upgrade 'pip>=25,<27'
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements.txt" starlette sse-starlette uvicorn

mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$UNIT_DIR" "$ROOT/cache_data" "$ROOT/samples"

if [[ ! -f "$CONFIG_DIR/fay.env" ]]; then
  sed \
    -e "s|FAY_BIND_HOST=127.0.0.1|FAY_BIND_HOST=$TAILNET_IP|" \
    -e "s|FAY_MCP_SSE_HOST=127.0.0.1|FAY_MCP_SSE_HOST=$TAILNET_IP|" \
    -e "s|%h|$HOME|g" \
    "$ROOT/deploy/dgx-spark/fay.env.example" > "$CONFIG_DIR/fay.env"
  chmod 600 "$CONFIG_DIR/fay.env"
fi

if [[ ! -f "$CONFIG_DIR/system.conf" ]]; then
  sed "s|__FAY_PUBLIC_URL__|http://$TAILNET_IP:5000|" \
    "$ROOT/deploy/dgx-spark/system.conf.example" > "$CONFIG_DIR/system.conf"
  chmod 600 "$CONFIG_DIR/system.conf"
fi

if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
  install -m 600 "$ROOT/deploy/dgx-spark/config.json" "$CONFIG_DIR/config.json"
fi

if [[ ! -f "$DATA_DIR/mcp_servers.json" ]]; then
  sed "s|__SPARK_STUDIO_ROOT__|$SPARK_STUDIO_ROOT|g" \
    "$ROOT/deploy/dgx-spark/mcp_servers.json.example" > "$DATA_DIR/mcp_servers.json"
fi
for state_file in mcp_tool_states.json mcp_prestart_tools.json; do
  if [[ ! -f "$DATA_DIR/$state_file" ]]; then
    printf '{}\n' > "$DATA_DIR/$state_file"
  fi
done

install -m 644 "$ROOT/deploy/dgx-spark/systemd/fay.service" "$UNIT_DIR/fay.service"
install -m 644 "$ROOT/deploy/dgx-spark/systemd/fay-asr-proxy.service" "$UNIT_DIR/fay-asr-proxy.service"
systemctl --user daemon-reload
systemctl --user enable --now fay-asr-proxy.service fay.service

printf 'Fay installed at %s and bound to %s\n' "$ROOT" "$TAILNET_IP"

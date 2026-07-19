# DGX Spark deployment

This deployment adapts the authors' reference topology to the Spark:

- Fay runs as the always-on conversation, memory, tool, voice, and avatar-control runtime.
- The Spark's existing OpenAI-compatible router provides the LLM.
- Existing Voxtral Realtime and Voxtral TTS services provide local ASR and speech.
- Fay connects to Spark Studio and its bundled schedule manager as MCP clients.
- Fay exposes memory, broadcast, and enabled upstream tools through its own MCP SSE endpoint.
- UE5/MetaHuman remains a Windows display client and connects to Fay's avatar WebSocket.

The services bind to the Spark's Tailscale address by default. They are not exposed on every LAN interface.

## Services

| Interface | Port | Purpose |
|---|---:|---|
| HTTP control/API | 5000 | Configuration, chat, status, and audio files |
| MCP administration | 5010 | Manage Fay's upstream MCP connections |
| MCP SSE | 8766 | Connect external agents to Fay |
| Remote voice WebSocket | 9001 | Remote microphone/speaker bridge |
| Remote voice TCP | 10001 | Native remote audio transport |
| Avatar WebSocket | 10002 | Audio, text, action, emotion, and lip data |
| Panel WebSocket | 10003 | Fay management UI events |

Run `deploy/dgx-spark/healthcheck.py` inside the Fay virtual environment to verify the full dependency chain.

The official `fay-ue5` reference client is Windows/UE 5.6. It cannot run natively on the Spark's ARM Linux host. Point a tailnet-connected Windows client at the Spark avatar WebSocket and HTTP audio URL.

## Live connection points

Get the Spark address with `tailscale ip -4`, then replace `<spark-tailnet-ip>` below.

- Management UI and OpenAI-compatible API: `http://<spark-tailnet-ip>:5000`
- Avatar renderer: `ws://<spark-tailnet-ip>:10002`
- Fay MCP server (legacy SSE transport): `http://<spark-tailnet-ip>:8766/sse`
- MCP connection manager: `http://<spark-tailnet-ip>:5010`

An avatar client registers itself after connecting:

```json
{"Username":"User","Output":true}
```

`Output: true` tells Fay to synthesize speech and send `Topic: human` messages containing the text, a fetchable WAV URL, duration, sentiment, and optional action. Keep the same `Username` in chat requests so replies are routed to that renderer.

External MCP clients should connect to the SSE URL above. Fay currently exposes its memory and broadcast tools plus namespaced tools from the configured upstream servers. The default Spark installation connects Spark Studio's creative tools and Fay's schedule manager. Upstreams are managed in `~/.local/share/fay/mcp/mcp_servers.json`; mutable MCP state is kept outside the Git checkout.

The HTTP API can also be used without an avatar:

```bash
curl http://<spark-tailnet-ip>:5000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"fay","user":"User","messages":[{"role":"user","content":"Hello"}]}'
```

## Operations

```bash
systemctl --user status fay.service fay-asr-proxy.service
systemctl --user restart fay.service fay-asr-proxy.service
journalctl --user -u fay.service -u fay-asr-proxy.service -f

cd ~/Workspace/01_Projects/Active/Fay
set -a; source ~/.config/fay/fay.env; set +a
.venv/bin/python deploy/dgx-spark/healthcheck.py
```

Both units are enabled, restart on failure, and continue across reboots through systemd user lingering. Configuration is in `~/.config/fay`; those files are mode `0600` and are not overwritten by repeated installer runs.

## Reference fidelity and the 3D boundary

The [official architecture](https://www.fay-agent.com/) makes Fay the conversation/voice/control backend and treats UE5/MetaHuman as a separate display client. The [`fay-ue5` repository](https://github.com/xszyou/fay-ue5) documents a 15-shape MPEG-4/OVR-style mouth set and includes a general MPEG-4 Face and Body Animation overview; it does not contain a separate Fay research paper.

Upstream Fay generates its detailed `Lips` sequence with a bundled Windows-only OVR executable. That executable cannot run on the Spark's ARM Linux host. The Spark deployment therefore supplies the renderer with working speech audio, timing, sentiment, and action signals, but does not claim server-generated OVR visemes. For a photorealistic result, run the official UE 5.6/MetaHuman client on a tailnet-connected Windows RTX machine and animate from the received audio, or add a supported facial-animation service such as Audio2Face between Fay and Unreal.

NVIDIA's current [Audio2Face-3D support matrix](https://docs.nvidia.com/ace/audio2face-3d-microservice/latest/text/support-matrix.html) does not list the DGX Spark GB10 as a pre-generated profile. It should be treated as a separate, validated integration project rather than silently added to this reliable base deployment.

The services have no application-layer authentication in this configuration. They are intentionally bound only to the Spark's Tailscale address; do not change the bind host to `0.0.0.0` without adding authentication and firewall rules.

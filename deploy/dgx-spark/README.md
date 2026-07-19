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
| MCP SSE | 8765 | Connect external agents to Fay |
| Remote voice WebSocket | 9001 | Remote microphone/speaker bridge |
| Remote voice TCP | 10001 | Native remote audio transport |
| Avatar WebSocket | 10002 | Audio, text, action, emotion, and lip data |
| Panel WebSocket | 10003 | Fay management UI events |

Run `deploy/dgx-spark/healthcheck.py` inside the Fay virtual environment to verify the full dependency chain.

The official `fay-ue5` reference client is Windows/UE 5.6. It cannot run natively on the Spark's ARM Linux host. Point a tailnet-connected Windows client at the Spark avatar WebSocket and HTTP audio URL.

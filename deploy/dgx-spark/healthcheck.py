#!/usr/bin/env python3
"""Return non-zero unless Fay and every required local dependency are ready."""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.request


def http_json(url: str, timeout: float = 3.0):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def tcp_ready(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> int:
    bind_host = os.environ.get("FAY_BIND_HOST", "127.0.0.1")
    checks = {}
    for name, host, port in (
        ("http", bind_host, 5000),
        ("avatar_websocket", bind_host, 10002),
        ("panel_websocket", bind_host, 10003),
        ("remote_audio", bind_host, 9001),
        ("mcp_admin", bind_host, 5010),
        ("mcp_sse", bind_host, int(os.environ.get("FAY_MCP_SSE_PORT", "8766"))),
        ("asr_proxy", "127.0.0.1", 10197),
    ):
        checks[name] = tcp_ready(host, port)

    for name, url in (
        ("llm_router", os.environ.get("FAY_LLM_HEALTH_URL", "http://127.0.0.1:5055/v1/models")),
        ("voxtral_asr", "http://127.0.0.1:4395/v1/models"),
        ("voxtral_tts", "http://127.0.0.1:4396/v1/models"),
    ):
        try:
            status, payload = http_json(url)
            checks[name] = status == 200 and bool(payload.get("data"))
        except Exception:
            checks[name] = False

    try:
        request = urllib.request.Request(
            "http://127.0.0.1:11435/v1/embeddings",
            data=json.dumps({"model": "nomic-embed-text:latest", "input": "health check"}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer local-spark"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            checks["embeddings"] = response.status == 200 and bool(payload.get("data", [{}])[0].get("embedding"))
    except Exception:
        checks["embeddings"] = False

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

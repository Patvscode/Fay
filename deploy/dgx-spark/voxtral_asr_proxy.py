#!/usr/bin/env python3
"""Bridge Fay's file-based FunASR protocol to vLLM Voxtral Realtime.

Fay sends ``{"url": "/path/to/utterance.wav"}`` over WebSocket. This
service reads only files below the configured cache directory, streams their
16 kHz mono PCM to Voxtral, and sends the final transcript back as text.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import wave
from pathlib import Path

import websockets


LOG = logging.getLogger("fay-voxtral-asr")


class VoxtralProxy:
    def __init__(self, runtime_url: str, model: str, allowed_root: Path):
        self.runtime_url = runtime_url
        self.model = model
        self.allowed_root = allowed_root.resolve()

    def _safe_audio_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve(strict=True)
        if path != self.allowed_root and self.allowed_root not in path.parents:
            raise ValueError(f"Audio path is outside FAY_ASR_ALLOWED_ROOT: {path}")
        return path

    @staticmethod
    def _read_pcm(path: Path) -> bytes:
        with wave.open(str(path), "rb") as source:
            if source.getnchannels() != 1 or source.getsampwidth() != 2 or source.getframerate() != 16000:
                raise ValueError("Fay ASR input must be mono 16-bit PCM at 16 kHz")
            return source.readframes(source.getnframes())

    async def transcribe(self, path: Path) -> str:
        audio = await asyncio.to_thread(self._read_pcm, path)
        transcript = ""
        async with websockets.connect(self.runtime_url, open_timeout=5, close_timeout=5) as runtime:
            while True:
                event = json.loads(await asyncio.wait_for(runtime.recv(), timeout=15))
                if event.get("type") == "session.created":
                    break
                if event.get("type") == "error":
                    raise RuntimeError(str(event.get("error") or event))

            await runtime.send(json.dumps({"type": "session.update", "model": self.model}))
            for offset in range(0, len(audio), 6400):
                chunk = base64.b64encode(audio[offset : offset + 6400]).decode("ascii")
                await runtime.send(json.dumps({"type": "input_audio_buffer.append", "audio": chunk}))
            await runtime.send(json.dumps({"type": "input_audio_buffer.commit", "final": False}))
            await runtime.send(json.dumps({"type": "input_audio_buffer.commit", "final": True}))

            while True:
                event = json.loads(await asyncio.wait_for(runtime.recv(), timeout=90))
                event_type = event.get("type")
                if event_type == "transcription.delta":
                    transcript += str(event.get("delta") or "")
                elif event_type == "transcription.done":
                    return " ".join(str(event.get("text") or transcript).split())
                elif event_type == "error":
                    raise RuntimeError(str(event.get("error") or event))

    async def handle(self, client, _path=None):
        async for message in client:
            if not isinstance(message, str):
                continue
            audio_path = None
            try:
                payload = json.loads(message)
                if not payload.get("url"):
                    continue
                audio_path = self._safe_audio_path(str(payload["url"]))
                transcript = await self.transcribe(audio_path)
                await client.send(transcript)
            except Exception as exc:
                LOG.exception("Transcription failed")
                await client.send("")
            finally:
                if audio_path is not None:
                    try:
                        audio_path.unlink(missing_ok=True)
                    except Exception:
                        LOG.warning("Could not remove temporary audio %s", audio_path)


async def run(args) -> None:
    proxy = VoxtralProxy(args.runtime_url, args.model, Path(args.allowed_root))
    async with websockets.serve(proxy.handle, args.host, args.port, ping_interval=20, ping_timeout=20):
        LOG.info("Fay Voxtral ASR proxy listening on ws://%s:%s", args.host, args.port)
        await asyncio.Future()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("FAY_ASR_PROXY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("FAY_ASR_PROXY_PORT", "10197")))
    parser.add_argument(
        "--runtime-url",
        default=os.environ.get("FAY_VOXTRAL_REALTIME_URL", "ws://127.0.0.1:4395/v1/realtime"),
    )
    parser.add_argument("--model", default=os.environ.get("FAY_VOXTRAL_REALTIME_MODEL", ""))
    parser.add_argument(
        "--allowed-root",
        default=os.environ.get("FAY_ASR_ALLOWED_ROOT", str(Path.cwd() / "cache_data")),
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("FAY_LOG_LEVEL", "INFO"))
    arguments = parse_args()
    if not arguments.model:
        raise SystemExit("FAY_VOXTRAL_REALTIME_MODEL is required")
    asyncio.run(run(arguments))

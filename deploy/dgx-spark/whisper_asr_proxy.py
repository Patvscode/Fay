#!/usr/bin/env python3
"""Bridge Fay's file-based ASR protocol to the existing local Whisper API."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path

import requests
import websockets


LOG = logging.getLogger("fay-whisper-asr")


class WhisperProxy:
    def __init__(
        self,
        api_url: str,
        model_name: str,
        language: str | None,
        upload_root: Path,
        allowed_root: Path,
        timeout: float,
    ):
        self.api_url = api_url
        self.model_name = model_name
        self.language = language
        self.upload_root = upload_root.resolve()
        self.allowed_root = allowed_root.resolve()
        self.timeout = timeout
        self.inference_lock = asyncio.Lock()

    def _safe_audio_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve(strict=True)
        if path != self.allowed_root and self.allowed_root not in path.parents:
            raise ValueError(f"Audio path is outside FAY_ASR_ALLOWED_ROOT: {path}")
        return path

    def _transcribe_sync(self, path: Path) -> str:
        copied_path = None
        try:
            with path.open("rb") as audio:
                response = requests.post(
                    self.api_url,
                    files={"audio": (path.name, audio, "audio/wav")},
                    data={
                        "model": self.model_name,
                        "language": self.language or "en",
                    },
                    timeout=self.timeout,
                )
            response.raise_for_status()
            result = response.json()
            copied_value = result.get("path")
            if isinstance(copied_value, str) and copied_value:
                candidate = Path(copied_value).resolve(strict=True)
                if (
                    candidate != self.upload_root
                    and self.upload_root in candidate.parents
                    and candidate.is_file()
                    and not candidate.is_symlink()
                ):
                    copied_path = candidate
            return " ".join(str(result.get("text") or "").split())
        finally:
            if copied_path is not None:
                try:
                    copied_path.unlink(missing_ok=True)
                except OSError:
                    LOG.warning("Could not remove copied Whisper input %s", copied_path)

    async def transcribe(self, path: Path) -> str:
        async with self.inference_lock:
            return await asyncio.to_thread(self._transcribe_sync, path)

    async def handle(self, client, _path=None):
        async for message in client:
            if not isinstance(message, str):
                continue
            audio_path = None
            try:
                payload = json.loads(message)
                if not isinstance(payload, dict) or not payload.get("url"):
                    continue
                audio_path = self._safe_audio_path(str(payload["url"]))
                await client.send(await self.transcribe(audio_path))
            except Exception:
                LOG.exception("Transcription failed")
                await client.send("")
            finally:
                if audio_path is not None:
                    try:
                        audio_path.unlink(missing_ok=True)
                    except OSError:
                        LOG.warning("Could not remove temporary audio %s", audio_path)


async def run(args) -> None:
    proxy = WhisperProxy(
        args.api_url,
        args.model,
        args.language or None,
        Path(args.upload_root),
        Path(args.allowed_root),
        args.timeout,
    )
    async with websockets.serve(
        proxy.handle,
        args.host,
        args.port,
        ping_interval=20,
        ping_timeout=20,
        max_size=16 * 1024,
    ):
        LOG.info(
            "Fay Whisper ASR proxy ready on ws://%s:%s (model=%s)",
            args.host,
            args.port,
            args.model,
        )
        await asyncio.Future()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", default=os.environ.get("FAY_ASR_PROXY_HOST", "127.0.0.1")
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FAY_ASR_PROXY_PORT", "10197")),
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get(
            "FAY_WHISPER_API_URL",
            "http://127.0.0.1:4397/api/voice/transcribe",
        ),
    )
    parser.add_argument(
        "--model", default=os.environ.get("FAY_WHISPER_MODEL", "base")
    )
    parser.add_argument(
        "--language", default=os.environ.get("FAY_WHISPER_LANGUAGE", "en")
    )
    parser.add_argument(
        "--upload-root",
        default=os.environ.get(
            "FAY_WHISPER_UPLOAD_ROOT",
            str(Path.home() / ".codex-studio-v2" / "voice"),
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("FAY_WHISPER_TIMEOUT", "90")),
    )
    parser.add_argument(
        "--allowed-root",
        default=os.environ.get(
            "FAY_ASR_ALLOWED_ROOT", str(Path.cwd() / "cache_data")
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("FAY_LOG_LEVEL", "INFO"))
    asyncio.run(run(parse_args()))

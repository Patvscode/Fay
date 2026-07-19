"""OpenAI-compatible text-to-speech adapter.

This keeps Fay's existing ``Speech.to_sample`` contract while allowing a
local service such as vLLM Omni/Voxtral to provide speech without cloud keys.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from utils import util


class Speech:
    def __init__(self):
        self.base_url = os.environ.get("FAY_OPENAI_TTS_BASE_URL", "http://127.0.0.1:4396/v1").rstrip("/")
        self.model = os.environ.get("FAY_OPENAI_TTS_MODEL", "").strip()
        self.voice = os.environ.get("FAY_OPENAI_TTS_VOICE", "cheerful_female").strip() or "cheerful_female"
        self.timeout = float(os.environ.get("FAY_OPENAI_TTS_TIMEOUT", "90"))

    def connect(self):
        return None

    def close(self):
        return None

    def _runtime_model(self) -> str:
        if self.model:
            return self.model
        response = requests.get(f"{self.base_url}/models", timeout=min(self.timeout, 10))
        response.raise_for_status()
        models = response.json().get("data") or []
        if not models:
            raise RuntimeError("The OpenAI-compatible TTS service reported no models")
        model = models[0]
        if isinstance(model, dict):
            return str(model.get("id") or model.get("model") or "").strip()
        return str(model).strip()

    def to_sample(self, text, style):
        del style  # The configured Voxtral voice already carries the speaking style.
        try:
            response = requests.post(
                f"{self.base_url}/audio/speech",
                json={
                    "model": self._runtime_model(),
                    "input": str(text),
                    "voice": self.voice,
                    "response_format": "wav",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            samples_dir = Path("samples")
            samples_dir.mkdir(parents=True, exist_ok=True)
            file_url = samples_dir / f"sample-{int(time.time() * 1000)}.wav"
            file_url.write_bytes(response.content)
            return str(file_url)
        except Exception as exc:
            util.log(1, f"[x] OpenAI-compatible speech conversion failed: {exc}")
            return None

"""Validation and wire-format helpers for constrained avatar actions."""

from __future__ import annotations

import math
from typing import Any, Dict, Tuple


ALLOWED_BEHAVIORS: Tuple[str, ...] = (
    "idle",
    "listen",
    "wave",
    "invite",
    "think",
    "warn",
    "nod",
    "shake",
    "explain",
)


def normalize_avatar_action(
    behavior: Any,
    intensity: Any = 0.5,
    duration: Any = 1.0,
) -> Dict[str, object]:
    """Return a bounded action or raise ValueError for untrusted input."""

    normalized_behavior = str(behavior or "").strip().lower()
    if normalized_behavior not in ALLOWED_BEHAVIORS:
        allowed = ", ".join(ALLOWED_BEHAVIORS)
        raise ValueError(f"behavior must be one of: {allowed}")

    try:
        normalized_intensity = float(intensity)
        normalized_duration = float(duration)
    except (TypeError, ValueError) as exc:
        raise ValueError("intensity and duration must be numbers") from exc

    if not math.isfinite(normalized_intensity) or not math.isfinite(normalized_duration):
        raise ValueError("intensity and duration must be finite")
    if not 0.0 <= normalized_intensity <= 1.0:
        raise ValueError("intensity must be between 0 and 1")
    if not 0.2 <= normalized_duration <= 10.0:
        raise ValueError("duration must be between 0.2 and 10 seconds")

    return {
        "behavior": normalized_behavior,
        "intensity": normalized_intensity,
        "duration": normalized_duration,
    }


def build_avatar_action_message(
    behavior: Any,
    intensity: Any = 0.5,
    duration: Any = 1.0,
    *,
    username: str = "User",
) -> Dict[str, object]:
    """Build the narrow Fay-to-renderer action-only message."""

    action = normalize_avatar_action(behavior, intensity, duration)
    return {
        "Topic": "human",
        "Data": {
            "Key": "action",
            "Time": action["duration"],
            "Action": {
                "code": f"mcp.{action['behavior']}",
                "behavior": action["behavior"],
                "affect": "neutral",
                "intensity": action["intensity"],
                "priority": 50,
                "sentimentHint": 0.0,
            },
        },
        "Username": (username or "User").strip() or "User",
    }

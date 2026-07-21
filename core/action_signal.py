from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple


RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "action_rules.csv"


@dataclass(frozen=True)
class ActionRule:
    code: str
    behavior: str
    affect: str
    intensity: float
    priority: int
    sentiment_hint: float
    keywords: Tuple[str, ...]


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _keyword_matches(normalized_text: str, keyword: str) -> bool:
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return False
    # English keywords must be complete tokens. A raw substring check made the
    # reject keyword "no" fire inside ordinary words such as "now". CJK and
    # punctuation-bearing phrases retain substring matching because they do
    # not use the same whitespace/token boundary convention.
    if re.fullmatch(r"[a-z0-9_]+", normalized_keyword):
        pattern = rf"(?<![a-z0-9_]){re.escape(normalized_keyword)}(?![a-z0-9_])"
        return re.search(pattern, normalized_text) is not None
    return normalized_keyword in normalized_text


@lru_cache(maxsize=1)
def load_action_rules() -> Tuple[ActionRule, ...]:
    try:
        with RULES_PATH.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            built_rules: List[ActionRule] = []
            for row in reader:
                try:
                    keywords = tuple(
                        k.strip() for k in row["keywords"].split("|") if k.strip()
                    )
                    built_rules.append(ActionRule(
                        code=row["code"],
                        behavior=row["behavior"],
                        affect=row["affect"],
                        intensity=float(row.get("intensity", 0.5)),
                        priority=int(row.get("priority", 0)),
                        sentiment_hint=float(row.get("sentimentHint", 0.0)),
                        keywords=keywords,
                    ))
                except (KeyError, TypeError, ValueError):
                    continue
    except OSError:
        return ()

    return tuple(built_rules)


def resolve_action_signal(text: str) -> Optional[Dict[str, object]]:
    normalized = _normalize_text(text)
    if not normalized:
        return None

    best_rule: Optional[ActionRule] = None
    best_matches: List[str] = []
    best_score = (-1, -1, -1)

    for rule in load_action_rules():
        matched_keywords = [
            keyword for keyword in rule.keywords if _keyword_matches(normalized, keyword)
        ]
        if not matched_keywords:
            continue

        score = (
            len(matched_keywords),
            max(len(keyword) for keyword in matched_keywords),
            rule.priority,
        )
        if score > best_score:
            best_rule = rule
            best_matches = matched_keywords
            best_score = score

    if best_rule is None:
        return None

    return {
        "code": best_rule.code,
        "behavior": best_rule.behavior,
        "affect": best_rule.affect,
        "intensity": best_rule.intensity,
        "priority": best_rule.priority,
        "matchedKeywords": best_matches,
        "sentimentHint": best_rule.sentiment_hint,
    }

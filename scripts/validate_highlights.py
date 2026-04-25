#!/usr/bin/env python3
"""Validate auto-highlight-video JSON manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_MIN_DURATION = 30.0
DEFAULT_MAX_DURATION = 90.0
REQUIRED_FIELDS = ("id", "title", "start", "end", "score", "reason", "risk", "edit_notes")
TIMECODE_RE = re.compile(r"^(?:(\d+):)?([0-5]?\d):([0-5]?\d)(?:\.(\d{1,3}))?$")


class ValidationError(Exception):
    """Raised when a highlight manifest is invalid."""


def parse_timecode(value: Any) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        seconds = float(value)
        if seconds < 0:
            raise ValidationError(f"time must be non-negative: {value!r}")
        return seconds

    if not isinstance(value, str):
        raise ValidationError(f"time must be seconds or HH:MM:SS.mmm: {value!r}")

    stripped = value.strip()
    if stripped.isdigit():
        return float(stripped)

    match = TIMECODE_RE.match(stripped)
    if not match:
        raise ValidationError(f"invalid timecode: {value!r}")

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    millis = match.group(4) or "0"
    return hours * 3600 + minutes * 60 + seconds + int(millis.ljust(3, "0")) / 1000


def load_highlights(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValidationError("manifest root must be a JSON object")
    return payload


def validate_highlights(
    payload: dict[str, Any],
    *,
    min_duration: float = DEFAULT_MIN_DURATION,
    max_duration: float = DEFAULT_MAX_DURATION,
    allow_overlap: bool = False,
) -> list[dict[str, Any]]:
    highlights = payload.get("highlights")
    if not isinstance(highlights, list):
        raise ValidationError("manifest must contain a highlights list")

    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(highlights):
        if not isinstance(item, dict):
            raise ValidationError(f"highlight {index} must be an object")

        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            raise ValidationError(f"highlight {index} missing required field(s): {', '.join(missing)}")

        clip_id = item["id"]
        if not isinstance(clip_id, str) or not clip_id.strip():
            raise ValidationError(f"highlight {index} id must be a non-empty string")
        if clip_id in seen_ids:
            raise ValidationError(f"Duplicate id: {clip_id}")
        seen_ids.add(clip_id)

        score = item["score"]
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 1 <= score <= 10:
            raise ValidationError(f"highlight {clip_id} score must be between 1 and 10")

        for field in ("title", "reason", "risk", "edit_notes"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValidationError(f"highlight {clip_id} {field} must be a non-empty string")

        start = parse_timecode(item["start"])
        end = parse_timecode(item["end"])
        duration = end - start
        if duration <= 0:
            raise ValidationError(f"highlight {clip_id} end must be after start")
        if duration < min_duration or duration > max_duration:
            raise ValidationError(
                f"highlight {clip_id} duration {duration:.3f}s outside "
                f"{min_duration:.3f}-{max_duration:.3f}s"
            )

        normalized.append({**item, "start_seconds": start, "end_seconds": end, "duration_seconds": duration})

    if not allow_overlap:
        ordered = sorted(normalized, key=lambda item: item["start_seconds"])
        for previous, current in zip(ordered, ordered[1:]):
            if current["start_seconds"] < previous["end_seconds"]:
                raise ValidationError(f"highlights overlap: {previous['id']} and {current['id']}")

    return normalized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an auto-highlight-video JSON manifest.")
    parser.add_argument("manifest", help="Path to highlight manifest JSON")
    parser.add_argument("--min-duration", type=float, default=DEFAULT_MIN_DURATION)
    parser.add_argument("--max-duration", type=float, default=DEFAULT_MAX_DURATION)
    parser.add_argument("--allow-overlap", action="store_true")
    args = parser.parse_args(argv)

    try:
        payload = load_highlights(args.manifest)
        clips = validate_highlights(
            payload,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            allow_overlap=args.allow_overlap,
        )
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {len(clips)} highlight(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

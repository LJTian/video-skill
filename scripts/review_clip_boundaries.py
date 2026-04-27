#!/usr/bin/env python3
"""Review highlight cut points against timestamped transcript cue boundaries."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.clean_vtt import TIMING_LINE_RE, clean_caption_text
    from scripts.validate_highlights import ValidationError, load_highlights, parse_timecode, validate_highlights
except ModuleNotFoundError:
    from clean_vtt import TIMING_LINE_RE, clean_caption_text
    from validate_highlights import ValidationError, load_highlights, parse_timecode, validate_highlights


@dataclass(frozen=True)
class TranscriptCue:
    start_seconds: float
    end_seconds: float
    text: str


def parse_vtt_cues(raw: str) -> list[TranscriptCue]:
    cues: list[TranscriptCue] = []
    current_start: str | None = None
    current_end: str | None = None
    current_text: list[str] = []

    def flush() -> None:
        nonlocal current_start, current_end, current_text
        if current_start is None or current_end is None:
            current_text = []
            return
        text = clean_caption_text(" ".join(current_text))
        if text:
            cues.append(TranscriptCue(parse_timecode(current_start), parse_timecode(current_end), text))
        current_start = None
        current_end = None
        current_text = []

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line == "WEBVTT" or line.startswith(("NOTE", "STYLE", "REGION")):
            continue
        timing = TIMING_LINE_RE.match(line)
        if timing:
            flush()
            current_start = timing.group("start")
            current_end = timing.group("end")
            current_text = []
            continue
        if current_start is not None:
            current_text.append(line)

    flush()
    return cues


def review_clip_boundaries(
    payload: dict[str, Any],
    transcript_text: str,
    *,
    lead_padding: float = 0.25,
    tail_padding: float = 0.5,
) -> list[dict[str, Any]]:
    clips = validate_highlights(payload)
    cues = parse_vtt_cues(transcript_text)
    issues: list[dict[str, Any]] = []

    for clip in clips:
        clip_id = str(clip["id"])
        start = float(clip["start_seconds"])
        end = float(clip["end_seconds"])

        start_cue = _containing_cue(cues, start)
        if start_cue is not None:
            issues.append(
                {
                    "clip_id": clip_id,
                    "boundary": "start",
                    "issue": "cuts_inside_transcript_cue",
                    "time": format_timecode(start),
                    "suggested_time": format_timecode(max(0.0, start_cue.start_seconds - lead_padding)),
                    "cue_start": format_timecode(start_cue.start_seconds),
                    "cue_end": format_timecode(start_cue.end_seconds),
                    "cue_text": start_cue.text,
                }
            )

        end_cue = _containing_cue(cues, end)
        if end_cue is not None:
            issues.append(
                {
                    "clip_id": clip_id,
                    "boundary": "end",
                    "issue": "cuts_inside_transcript_cue",
                    "time": format_timecode(end),
                    "suggested_time": format_timecode(end_cue.end_seconds + tail_padding),
                    "cue_start": format_timecode(end_cue.start_seconds),
                    "cue_end": format_timecode(end_cue.end_seconds),
                    "cue_text": end_cue.text,
                }
            )

    return issues


def format_timecode(seconds: float) -> str:
    millis_total = int(round(seconds * 1000))
    whole_seconds, millis = divmod(millis_total, 1000)
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def _containing_cue(cues: list[TranscriptCue], seconds: float) -> TranscriptCue | None:
    for cue in cues:
        if cue.start_seconds < seconds < cue.end_seconds:
            return cue
    return None


def _print_issues(issues: list[dict[str, Any]]) -> None:
    for issue in issues:
        print(
            f"{issue['clip_id']} {issue['boundary']} {issue['time']} cuts inside "
            f"{issue['cue_start']} --> {issue['cue_end']}; "
            f"suggest {issue['suggested_time']}: {issue['cue_text']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review highlight cut points against transcript cue boundaries.")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("transcript", help="Timestamped WebVTT transcript")
    parser.add_argument("--lead-padding", type=float, default=0.25, help="Seconds to pad before a cue for start cuts")
    parser.add_argument("--tail-padding", type=float, default=0.5, help="Seconds to pad after a cue for end cuts")
    parser.add_argument("--json", action="store_true", help="Print issues as JSON")
    args = parser.parse_args(argv)

    try:
        payload = load_highlights(args.manifest)
        transcript_text = Path(args.transcript).read_text(encoding="utf-8")
        issues = review_clip_boundaries(
            payload,
            transcript_text,
            lead_padding=args.lead_padding,
            tail_padding=args.tail_padding,
        )
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"issues": issues}, indent=2))
    elif issues:
        _print_issues(issues)
    else:
        print("OK: clip boundaries do not cut through transcript cues")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

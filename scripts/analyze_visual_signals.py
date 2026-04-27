#!/usr/bin/env python3
"""Generate visual review commands for highlight candidates."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.export_clips import safe_slug
    from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights
except ModuleNotFoundError:
    from export_clips import safe_slug
    from validate_highlights import ValidationError, load_highlights, validate_highlights


def sample_times(clip: dict[str, Any], *, samples: int = 3) -> list[float]:
    if samples < 1:
        raise ValueError("samples must be at least 1")

    start = float(clip["start_seconds"])
    end = float(clip["end_seconds"])
    if samples == 1:
        return [start]

    near_end = max(start, end - 0.001)
    step = (near_end - start) / (samples - 1)
    return [round(start + step * index, 3) for index in range(samples)]


def build_frame_commands(
    video_path: Path,
    clip: dict[str, Any],
    output_dir: Path,
    *,
    samples: int = 3,
    ffmpeg: str = "ffmpeg",
) -> list[list[str]]:
    clip_id = safe_slug(str(clip["id"]), fallback="clip-id", max_length=32)
    commands = []
    for index, timestamp in enumerate(sample_times(clip, samples=samples), start=1):
        output_path = output_dir / f"{clip_id}-{index:03d}.jpg"
        commands.append(
            [
                ffmpeg,
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output_path),
            ]
        )
    return commands


def build_blackdetect_command(video_path: Path, clip: dict[str, Any], *, ffmpeg: str = "ffmpeg") -> list[str]:
    start = float(clip["start_seconds"])
    duration = float(clip["end_seconds"]) - start
    return [
        ffmpeg,
        "-ss",
        f"{start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-vf",
        "blackdetect=d=0.5:pix_th=0.10",
        "-an",
        "-f",
        "null",
        "-",
    ]


def build_visual_report(
    video_path: Path,
    clips: list[dict[str, Any]],
    output_dir: Path,
    *,
    samples: int = 3,
    ffmpeg: str = "ffmpeg",
) -> dict[str, Any]:
    return {
        "video": str(video_path),
        "frame_output_dir": str(output_dir),
        "clips": [
            {
                "id": clip["id"],
                "title": clip["title"],
                "sample_times": sample_times(clip, samples=samples),
                "frame_commands": build_frame_commands(video_path, clip, output_dir, samples=samples, ffmpeg=ffmpeg),
                "blackdetect_command": build_blackdetect_command(video_path, clip, ffmpeg=ffmpeg),
                "review_notes": [
                    "Check for black frames, scene changes, unreadable slides, and speaker visibility.",
                    "Treat visual signals as review evidence, not as a replacement for timestamped transcript analysis.",
                ],
            }
            for clip in clips
        ],
    }


def analyze_visual_signals(
    video_path: Path,
    manifest_path: Path,
    output_dir: Path,
    *,
    samples: int = 3,
    dry_run: bool = False,
    ffmpeg: str = "ffmpeg",
) -> dict[str, Any]:
    payload = load_highlights(manifest_path)
    clips = validate_highlights(payload)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_visual_report(video_path, clips, output_dir, samples=samples, ffmpeg=ffmpeg)

    if dry_run:
        for clip_report in report["clips"]:
            for command in clip_report["frame_commands"]:
                print(" ".join(_shell_quote(part) for part in command))
            print(" ".join(_shell_quote(part) for part in clip_report["blackdetect_command"]))
    else:
        for clip_report in report["clips"]:
            for command in clip_report["frame_commands"]:
                subprocess.run(command, check=True)
    return report


def _shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate visual review signals for highlight clips.")
    parser.add_argument("video", help="Source video path")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("--output-dir", default="visual-review-frames", help="Directory for representative frames")
    parser.add_argument("--samples", type=int, default=3, help="Representative frame count per clip")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without extracting frames")
    parser.add_argument("--json", action="store_true", help="Print the visual review report as JSON")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path")
    args = parser.parse_args(argv)

    try:
        report = analyze_visual_signals(
            Path(args.video),
            Path(args.manifest),
            Path(args.output_dir),
            samples=args.samples,
            dry_run=args.dry_run,
            ffmpeg=args.ffmpeg,
        )
    except (OSError, ValueError, ValidationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

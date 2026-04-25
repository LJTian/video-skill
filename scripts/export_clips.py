#!/usr/bin/env python3
"""Export clips from an auto-highlight-video JSON manifest with ffmpeg."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights
except ModuleNotFoundError:
    from validate_highlights import ValidationError, load_highlights, validate_highlights


def safe_slug(value: str, *, fallback: str = "clip", max_length: int = 64) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        return fallback
    return slug[:max_length].rstrip("-") or fallback


def build_output_path(output_dir: Path, clip: dict[str, Any]) -> Path:
    clip_id = safe_slug(str(clip["id"]), fallback="clip-id", max_length=32)
    title = safe_slug(str(clip["title"]), fallback="highlight", max_length=64)
    return output_dir / f"{clip_id}-{title}.mp4"


def build_ffmpeg_command(
    video_path: Path,
    output_path: Path,
    clip: dict[str, Any],
    *,
    reencode: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    start = float(clip["start_seconds"])
    duration = float(clip["end_seconds"]) - start
    command = [
        ffmpeg,
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration:.3f}",
        "-map",
        "0",
    ]
    if reencode:
        command.extend(["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k"])
    else:
        command.extend(["-c", "copy"])
    command.append(str(output_path))
    return command


def export_clips(
    video_path: Path,
    manifest_path: Path,
    output_dir: Path,
    *,
    dry_run: bool = False,
    reencode: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[list[str]]:
    payload = load_highlights(manifest_path)
    clips = validate_highlights(payload)
    output_dir.mkdir(parents=True, exist_ok=True)

    commands = []
    for clip in clips:
        output_path = build_output_path(output_dir, clip)
        command = build_ffmpeg_command(video_path, output_path, clip, reencode=reencode, ffmpeg=ffmpeg)
        commands.append(command)
        if dry_run:
            print(" ".join(_shell_quote(part) for part in command))
        else:
            subprocess.run(command, check=True)
    return commands


def _shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export highlight clips from a JSON manifest.")
    parser.add_argument("video", help="Source video path")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("--output-dir", default="highlight-clips", help="Directory for exported clips")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without executing them")
    parser.add_argument("--reencode", action="store_true", help="Re-encode clips for frame-accurate cuts")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path")
    args = parser.parse_args(argv)

    video_path = Path(args.video)
    if not video_path.exists() and not args.dry_run:
        print(f"ERROR: video file does not exist: {video_path}", file=sys.stderr)
        return 1

    try:
        export_clips(
            video_path,
            Path(args.manifest),
            Path(args.output_dir),
            dry_run=args.dry_run,
            reencode=args.reencode,
            ffmpeg=args.ffmpeg,
        )
    except (OSError, ValidationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render exported highlight clips into platform-ready formats."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.export_clips import build_output_path as build_base_clip_path
    from scripts.export_clips import safe_slug
    from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights
except ModuleNotFoundError:
    from export_clips import build_output_path as build_base_clip_path
    from export_clips import safe_slug
    from validate_highlights import ValidationError, load_highlights, validate_highlights


ASPECT_PRESETS = {
    "vertical": (1080, 1920),
    "9:16": (1080, 1920),
    "square": (1080, 1080),
    "1:1": (1080, 1080),
    "landscape": (1920, 1080),
    "16:9": (1920, 1080),
}


def build_video_filter(aspect: str, *, subtitles: Path | None = None) -> str:
    try:
        width, height = ASPECT_PRESETS[aspect]
    except KeyError as exc:
        raise ValueError(f"unsupported aspect: {aspect}") from exc

    filters = [f"scale={width}:{height}:force_original_aspect_ratio=increase", f"crop={width}:{height}"]
    if subtitles is not None:
        filters.append(f"subtitles={subtitles}")
    return ",".join(filters)


def build_output_path(output_dir: Path, clip: dict[str, Any], profile: str) -> Path:
    clip_id = safe_slug(str(clip["id"]), fallback="clip-id", max_length=32)
    title = safe_slug(str(clip["title"]), fallback="highlight", max_length=64)
    profile_slug = safe_slug(profile, fallback="profile", max_length=24)
    return output_dir / f"{clip_id}-{title}-{profile_slug}.mp4"


def build_platform_command(
    input_path: Path,
    output_path: Path,
    *,
    aspect: str,
    subtitles: Path | None = None,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    return [
        ffmpeg,
        "-y",
        "-i",
        str(input_path),
        "-vf",
        build_video_filter(aspect, subtitles=subtitles),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def render_platform_clips(
    manifest_path: Path,
    input_dir: Path,
    output_dir: Path,
    *,
    aspect: str = "vertical",
    profile: str | None = None,
    subtitles: Path | None = None,
    dry_run: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[list[str]]:
    payload = load_highlights(manifest_path)
    clips = validate_highlights(payload)
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_name = profile or aspect
    commands = []
    for clip in clips:
        input_path = build_base_clip_path(input_dir, clip)
        output_path = build_output_path(output_dir, clip, profile_name)
        command = build_platform_command(input_path, output_path, aspect=aspect, subtitles=subtitles, ffmpeg=ffmpeg)
        commands.append(command)
        if dry_run:
            print(" ".join(_shell_quote(part) for part in command))
        else:
            if not input_path.exists():
                raise FileNotFoundError(f"input clip does not exist: {input_path}")
            subprocess.run(command, check=True)
    return commands


def _shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render exported highlight clips for platform delivery.")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("--input-dir", default="highlight-clips", help="Directory containing base exported clips")
    parser.add_argument("--output-dir", default="platform-clips", help="Directory for rendered platform clips")
    parser.add_argument("--aspect", default="vertical", choices=sorted(ASPECT_PRESETS), help="Target aspect preset")
    parser.add_argument("--profile", help="Profile name used in output filenames")
    parser.add_argument("--subtitles", help="Optional subtitle file to burn into every output")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without executing them")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path")
    args = parser.parse_args(argv)

    try:
        render_platform_clips(
            Path(args.manifest),
            Path(args.input_dir),
            Path(args.output_dir),
            aspect=args.aspect,
            profile=args.profile,
            subtitles=Path(args.subtitles) if args.subtitles else None,
            dry_run=args.dry_run,
            ffmpeg=args.ffmpeg,
        )
    except (OSError, ValueError, ValidationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

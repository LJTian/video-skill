#!/usr/bin/env python3
"""Export a compilation video from highlight clips."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.export_clips import build_output_path
    from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights
except ModuleNotFoundError:
    from export_clips import build_output_path
    from validate_highlights import ValidationError, load_highlights, validate_highlights


def sort_clips(clips: list[dict[str, Any]], *, order: str = "manifest") -> list[dict[str, Any]]:
    if order == "manifest":
        return list(clips)
    if order == "score":
        return sorted(clips, key=lambda clip: float(clip["score"]), reverse=True)
    raise ValueError(f"unsupported compilation order: {order}")


def build_concat_lines(clips: list[dict[str, Any]], input_dir: Path) -> list[str]:
    return [f"file '{_escape_concat_path(build_output_path(input_dir, clip))}'" for clip in clips]


def build_compilation_command(
    concat_path: Path,
    output_path: Path,
    *,
    reencode: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    command = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path)]
    if reencode:
        command.extend(["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k"])
    else:
        command.extend(["-c", "copy"])
    command.append(str(output_path))
    return command


def export_compilation(
    manifest_path: Path,
    input_dir: Path,
    output_path: Path,
    *,
    order: str = "manifest",
    concat_path: Path | None = None,
    dry_run: bool = False,
    reencode: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    payload = load_highlights(manifest_path)
    clips = sort_clips(validate_highlights(payload), order=order)
    actual_concat_path = concat_path or output_path.with_suffix(".concat.txt")
    lines = build_concat_lines(clips, input_dir)
    command = build_compilation_command(actual_concat_path, output_path, reencode=reencode, ffmpeg=ffmpeg)

    if dry_run:
        for line in lines:
            print(line)
        print(" ".join(_shell_quote(part) for part in command))
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        actual_concat_path.parent.mkdir(parents=True, exist_ok=True)
        actual_concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run(command, check=True)
    return command


def _escape_concat_path(path: Path) -> str:
    return str(path).replace("'", "'\\''")


def _shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export a compilation video from highlight clips.")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("--input-dir", default="highlight-clips", help="Directory containing exported clips")
    parser.add_argument("--output", default="highlight-compilation.mp4", help="Compilation output path")
    parser.add_argument("--concat-path", help="Path for ffmpeg concat list")
    parser.add_argument("--order", default="manifest", choices=("manifest", "score"), help="Clip ordering")
    parser.add_argument("--dry-run", action="store_true", help="Print concat list and ffmpeg command")
    parser.add_argument("--reencode", action="store_true", help="Re-encode compilation output")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path")
    args = parser.parse_args(argv)

    try:
        export_compilation(
            Path(args.manifest),
            Path(args.input_dir),
            Path(args.output),
            order=args.order,
            concat_path=Path(args.concat_path) if args.concat_path else None,
            dry_run=args.dry_run,
            reencode=args.reencode,
            ffmpeg=args.ffmpeg,
        )
    except (OSError, ValueError, ValidationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

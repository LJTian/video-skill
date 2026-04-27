#!/usr/bin/env python3
"""Convert WebVTT captions into timestamped plain-text lines."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


TIMING_LINE_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})(?:\s+.*)?$"
)
INLINE_TIMING_RE = re.compile(r"<\d{2}:\d{2}(?::\d{2})?\.\d{3}>")
TAG_RE = re.compile(r"</?[^>]+>")


def clean_caption_text(value: str) -> str:
    value = INLINE_TIMING_RE.sub("", value)
    value = TAG_RE.sub("", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def clean_vtt_text(raw: str) -> list[str]:
    lines = raw.splitlines()
    output: list[str] = []
    current_start: str | None = None
    current_end: str | None = None
    current_text: list[str] = []
    previous_text: str | None = None

    def flush() -> None:
        nonlocal current_start, current_end, current_text, previous_text
        if current_start is None or current_end is None:
            current_text = []
            return
        text = clean_caption_text(" ".join(current_text))
        if text and text != previous_text:
            output.append(f"[{current_start} --> {current_end}] {text}")
            previous_text = text
        current_start = None
        current_end = None
        current_text = []

    for raw_line in lines:
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
        if current_start is None:
            continue
        current_text.append(line)

    flush()
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean WebVTT captions into timestamped plain text.")
    parser.add_argument("input", help="Input .vtt file")
    parser.add_argument("-o", "--output", help="Output text file; defaults to stdout")
    args = parser.parse_args(argv)

    text = Path(args.input).read_text(encoding="utf-8")
    cleaned = "\n".join(clean_vtt_text(text))
    if args.output:
        Path(args.output).write_text(cleaned + ("\n" if cleaned else ""), encoding="utf-8")
    else:
        print(cleaned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

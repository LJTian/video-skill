#!/usr/bin/env python3
"""Generate reviewable social publishing assets from highlight manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights
except ModuleNotFoundError:
    from validate_highlights import ValidationError, load_highlights, validate_highlights


STOPWORDS = {
    "about",
    "after",
    "from",
    "into",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "with",
    "why",
}


def suggest_hashtags(title: str, *, platform: str, limit: int = 4) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", title.lower())
    tags = []
    for word in words:
        if len(word) < 4 or word in STOPWORDS:
            continue
        tag = f"#{word}"
        if tag not in tags:
            tags.append(tag)
        if len(tags) >= limit - 1:
            break

    platform_tag = "#" + re.sub(r"[^A-Za-z0-9]+", "", platform.lower())
    if platform_tag != "#" and platform_tag not in tags:
        tags.append(platform_tag)
    return tags[:limit]


def build_publish_asset(
    clip: dict[str, Any],
    *,
    platform: str,
    audience: str = "general viewers",
) -> dict[str, Any]:
    title = str(clip["title"]).strip()
    reason = str(clip["reason"]).strip()
    risk = str(clip["risk"]).strip()
    edit_notes = str(clip["edit_notes"]).strip()
    return {
        "id": clip["id"],
        "platform": platform,
        "title": title,
        "description": f"For {audience}: {reason}",
        "caption": f"{title}. Key takeaway: {reason}",
        "hashtags": suggest_hashtags(title, platform=platform),
        "cover_suggestion": "Pick a clear frame near the opening hook where the speaker or key slide is visible.",
        "review_items": [
            f"Review editorial risk: {risk}",
            f"Review cut notes: {edit_notes}",
            "Confirm title and caption do not change the speaker's meaning.",
        ],
    }


def generate_publish_assets(
    manifest_path: Path,
    *,
    platform: str,
    audience: str = "general viewers",
) -> dict[str, Any]:
    payload = load_highlights(manifest_path)
    clips = validate_highlights(payload)
    return {
        "version": 1,
        "platform": platform,
        "audience": audience,
        "assets": [build_publish_asset(clip, platform=platform, audience=audience) for clip in clips],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate reviewable publishing assets from a highlight manifest.")
    parser.add_argument("manifest", help="Highlight manifest JSON")
    parser.add_argument("--platform", default="Shorts", help="Target platform label")
    parser.add_argument("--audience", default="general viewers", help="Target audience description")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args(argv)

    try:
        payload = generate_publish_assets(Path(args.manifest), platform=args.platform, audience=args.audience)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

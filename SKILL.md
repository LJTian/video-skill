---
name: auto-highlight-video
description: Use when the user wants AI-assisted highlight selection, automatic clip extraction, short-video cuts, or multiple high-value clips from long videos such as podcasts, courses, interviews, lectures, webinars, or narrated recordings.
---

# Auto Highlight Video

Use AI for editorial judgment and local scripts for deterministic execution. Treat timestamped transcripts as the primary evidence, validate a structured highlight manifest before export, then verify the exported media artifacts before calling the work complete.

## Inputs

Require one of:

- Source video path.
- Public video URL with permission to download or process it.

Also require a timestamped transcript path, downloadable timestamped subtitles, or a clear plan to generate timestamped transcript data before selecting highlights.

Accept transcript formats that preserve time ranges per utterance or segment, such as JSON, SRT, VTT, or a table with start/end times. If the transcript has no timestamps, stop and ask for timestamped data; do not invent precise cut points.

Optional:

- Target audience or platform.
- Desired number of clips.
- Minimum and maximum duration.
- Landscape 16:9, vertical 9:16, or another delivery format.
- Burned subtitles, clean video, titles, captions, descriptions, or summaries.
- Platform target such as Shorts, TikTok, Reels, Bilibili, WeChat Channels, or internal review.
- Topics to prioritize or avoid.
- Intro/outro/context to include or avoid.

## Workflow

1. Acquire source
   - If the user provides a local file, confirm it exists.
   - If the user provides a URL, read `references/source-acquisition.md`; check `yt-dlp`, `ffmpeg`, and `ffprobe`.
   - For URLs, probe metadata and download timestamped subtitles with `--skip-download` before downloading the full video.
   - For YouTube auth or bot blocks, try `--cookies-from-browser`; if that fails, ask for Netscape-format `cookies.txt`. Never print cookie contents.
   - Use `ffprobe` when available to collect duration, resolution, frame rate, and audio streams.
   - Note whether the source is landscape, portrait, or mixed.

2. Inspect the transcript
   - Confirm every usable segment has a start and end time.
   - Prefer timestamped VTT, SRT, JSON, or JSON3 subtitles. If preferred-language subtitles fail, use another language only if it is adequate for editorial judgment.
   - For YouTube auto-captions, clean rolling duplicate captions and inline tags with `python3 scripts/clean_vtt.py captions.vtt -o captions.clean.txt`.
   - Identify the language, speaker labels, topic shifts, and long silences if present.
   - Keep the original transcript available for checking context before finalizing cuts.
   - If there are no timestamped captions or transcript segments, generate a timestamped transcript before selecting highlights.

3. Select candidate highlights
   - Prefer 30-90 second standalone clips.
   - Find strong claims, clear explanations, stories, surprising turns, emotional peaks, memorable phrases, and dense teaching moments.
   - Avoid clips that require heavy prior context, distort the speaker, expose private information, or create copyright or safety concerns.
   - Include a short lead-in and tail when needed so sentence boundaries are not clipped.

4. Score and structure the decisions
   - Score each candidate from 1 to 10.
   - Recommend export for clips scoring 7 or higher unless the user asks for a broader set.
   - Write a JSON manifest that follows `references/highlight-schema.md`.
   - Include `reason`, `risk`, and `edit_notes` for every clip so the user can audit the editorial choice.

5. Validate before export
   - Run `python3 scripts/validate_highlights.py <manifest.json>`.
   - Fix the JSON if validation fails.
   - Do not run boundary review or export until validation passes.

6. Review clip boundaries
   - Run `python3 scripts/review_clip_boundaries.py <manifest.json> <transcript.vtt>` when a VTT transcript is available.
   - Treat any reported start or end cut inside a transcript cue as a blocker for export, because it can clip sentence boundaries or leave the speaker unfinished.
   - Adjust the manifest to a natural cue, sentence, or speaker boundary, then rerun the review.
   - Do not run `scripts/export_clips.py` until validation and boundary review both pass.

7. Export clips
   - Run a dry run first:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --dry-run
```

   - If the commands look correct, export:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips
```

   - Use `--reencode` when frame accuracy, broad playback compatibility, platform upload, or unusual source codecs such as VP9/Opus matter more than speed. For deliverable MP4 clips, prefer H.264 video plus AAC audio.

8. Verify exported media
   - Read `references/output-verification.md`.
   - Confirm the output file count equals the manifest highlight count.
   - Use `ffprobe` to confirm every clip has expected duration plus video and audio streams.
   - Run a decode check such as `ffmpeg -v error -i highlight-clips/clip.mp4 -f null -`.
   - Do not treat "ffmpeg exited 0" as proof that the deliverable is usable.

9. Review production quality
   - Read `references/quality-review.md`.
   - Make or inspect a contact sheet when possible, and check visual consistency across clips.
   - Confirm the subtitle policy is consistent: all clips use clean subtitles, or none do, unless the user requested mixed output.
   - For deliverables, ask for human review when editorial fit, speaker meaning, pacing, or platform packaging cannot be proven from automated checks.

## Clip Quality Rules

Good clips usually have:

- A clear hook in the first 5-10 seconds.
- One complete idea, story, argument, or explanation.
- Natural start and end points near sentence boundaries.
- Enough context to be understood by someone who did not watch the full video.
- Low risk of privacy issues, harmful misrepresentation, or misleading edits.

Weak clips usually have:

- A punchline without setup.
- A setup without payoff.
- Too much dependency on slides or visual details not described in speech.
- Mostly filler, greetings, housekeeping, or transitions.
- Interesting content that starts before or ends after the proposed cut.

## Manifest Format

Read `references/highlight-schema.md` when creating or reviewing the highlight JSON. Keep `id` values stable after the user reviews them, because exported filenames are derived from `id` and `title`.

## Platform Output

Read `references/platform-presets.md` when the output needs vertical framing, burned subtitles, social captions, titles, summaries, or platform-specific packaging. Do not assume landscape no-subtitle clips are the final format when the user asks for social-ready assets.

## Phase 2 Packaging

After base clips pass validation, export, media verification, and production quality review, run only the packaging steps the user requested:

- Use `python3 scripts/render_platform_clips.py <manifest.json> --input-dir highlight-clips --output-dir platform-clips --aspect vertical --dry-run` before producing vertical, square, landscape, or burned-subtitle variants.
- Use `python3 scripts/analyze_visual_signals.py input.mp4 <manifest.json> --dry-run --json` to generate representative-frame and black-frame review commands when visual quality affects the decision.
- Use `python3 scripts/export_compilation.py <manifest.json> --input-dir highlight-clips --output highlight-compilation.mp4 --dry-run` before creating a compilation video.
- Use `python3 scripts/generate_publish_assets.py <manifest.json> --platform Shorts --audience "target viewers"` to create reviewable titles, descriptions, captions, hashtags, cover suggestions, and manual review items.

Do not let packaging steps change the original cut decisions silently. If visual review, platform framing, subtitles, or publishing copy reveal a problem, update the manifest or report the risk before exporting final assets.

## Quality Review

Read `references/quality-review.md` before calling exported clips final. Media validity is not the same as a good highlight package.

## Credential Safety

If cookies, tokens, browser profiles, auth headers, API keys, private keys, or exported credential files are used:

- Never print their contents.
- Store them only in the working directory or a user-provided path.
- Do not include credential files in manifests or output bundles.
- Mention cleanup or deletion in the final response when appropriate.

## Common Failure Branches

- No timestamped subtitles: generate a timestamped transcript before selecting highlights.
- Poor subtitle quality: inspect samples before trusting it.
- YouTube subtitle HTTP 429: proceed with an adequate available language or retry later.
- Download blocked: request `cookies.txt` or a local video file.
- One clip export fails: report the clip id, command, and stderr summary; retry only that clip after fixing the cause.

## Script Notes

- `scripts/validate_highlights.py` accepts a manifest path and checks required fields, score range, timecodes, duration bounds, duplicate IDs, and overlap.
- `scripts/review_clip_boundaries.py` compares manifest cut points with VTT transcript cues and reports start or end cuts that land inside active speech.
- `scripts/export_clips.py` reads a valid manifest and calls `ffmpeg` once per clip.
- `scripts/clean_vtt.py` converts WebVTT captions to clean timestamped text lines for transcript review.
- `scripts/render_platform_clips.py` renders existing clips into platform-specific aspect ratios and optional burned subtitles.
- `scripts/analyze_visual_signals.py` generates representative-frame extraction and black-frame review commands for candidate clips.
- `scripts/export_compilation.py` builds an `ffmpeg` concat workflow for highlight compilation videos.
- `scripts/generate_publish_assets.py` creates reviewable social publishing metadata without uploading anything.
- Default export uses stream copy for speed. Use `--reencode` for more accurate cuts or when stream copy produces playback issues.
- If `ffmpeg` fails for one clip, report the failing clip id, command, and stderr summary before retrying.

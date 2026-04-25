---
name: auto-highlight-video
description: Use when the user wants AI-assisted highlight selection, automatic clip extraction, short-video cuts, or multiple high-value clips from long videos such as podcasts, courses, interviews, lectures, webinars, or narrated recordings.
---

# Auto Highlight Video

Use AI for editorial judgment and local scripts for deterministic execution. Treat transcripts as the primary evidence, then validate a structured highlight manifest before exporting any clips.

## Inputs

Require:

- Source video path.
- Timestamped transcript path, or a clear plan to generate one before selecting highlights.

Accept transcript formats that preserve time ranges per utterance or segment, such as JSON, SRT, VTT, or a table with start/end times. If the transcript has no timestamps, stop and ask for timestamped data; do not invent precise cut points.

Optional:

- Target audience or platform.
- Desired number of clips.
- Minimum and maximum duration.
- Topics to prioritize or avoid.

## Workflow

1. Inspect the video
   - Confirm the file exists.
   - Use `ffprobe` when available to collect duration, resolution, frame rate, and audio streams.
   - Note whether the source is landscape, portrait, or mixed.

2. Inspect the transcript
   - Confirm every usable segment has a start and end time.
   - Identify the language, speaker labels, topic shifts, and long silences if present.
   - Keep the original transcript available for checking context before finalizing cuts.

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
   - Do not run `scripts/export_clips.py` until validation passes.

6. Export clips
   - Run a dry run first:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --dry-run
```

   - If the commands look correct, export:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips
```

   - Use `--reencode` when frame-accurate cuts matter more than speed.

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

## Script Notes

- `scripts/validate_highlights.py` accepts a manifest path and checks required fields, score range, timecodes, duration bounds, duplicate IDs, and overlap.
- `scripts/export_clips.py` reads a valid manifest and calls `ffmpeg` once per clip.
- Default export uses stream copy for speed. Use `--reencode` for more accurate cuts or when stream copy produces playback issues.
- If `ffmpeg` fails for one clip, report the failing clip id, command, and stderr summary before retrying.

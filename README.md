# Auto Highlight Video Skill

Codex skill source for finding and exporting high-value clips from long videos,
podcasts, lectures, interviews, webinars, and narrated recordings.

The skill uses AI for editorial judgment and local Python scripts for
deterministic validation and `ffmpeg` execution. A timestamped transcript is the
primary input for highlight selection; a JSON manifest is the contract between
the AI decisions and clip export.

## What It Does

- Guides Codex through inspecting a source video and timestamped transcript.
- Selects standalone highlight candidates, usually 30-90 seconds each.
- Scores each candidate and records the reason, risk, and edit notes.
- Validates the highlight manifest before any clips are exported.
- Exports clips with `ffmpeg`, using stream copy by default or re-encoding when
  frame accuracy matters.

## Repository Layout

```text
.
|-- SKILL.md
|-- references/
|   `-- highlight-schema.md
|-- scripts/
|   |-- export_clips.py
|   `-- validate_highlights.py
`-- tests/
    |-- test_export_clips.py
    |-- test_skill_docs.py
    `-- test_validate_highlights.py
```

## Requirements

- Python 3.10 or newer.
- `ffmpeg` for exporting clips.
- `ffprobe` is recommended for video inspection when the skill is used.

The Python scripts only use the standard library.

## Highlight Manifest

Create a JSON manifest that follows
[`references/highlight-schema.md`](references/highlight-schema.md). Minimal
shape:

```json
{
  "version": 1,
  "source": {
    "video": "talk.mp4",
    "transcript": "talk.transcript.json"
  },
  "highlights": [
    {
      "id": "clip-01",
      "title": "Why latency budgets matter",
      "start": "00:03:12.000",
      "end": "00:04:18.500",
      "score": 8,
      "reason": "The speaker gives a complete explanation with a clear takeaway.",
      "risk": "Low risk. The clip is self-contained.",
      "edit_notes": "Start after the setup sentence and end before the next topic."
    }
  ]
}
```

## Validate A Manifest

Run validation before exporting:

```bash
python3 scripts/validate_highlights.py highlights.json
```

The validator checks required fields, score range, timecodes, default duration
bounds, duplicate IDs, and overlapping clips.

## Export Clips

Preview the generated `ffmpeg` commands first:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --dry-run
```

Export clips after the dry run looks correct:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips
```

Use `--reencode` for more accurate cuts:

```bash
python3 scripts/export_clips.py input.mp4 highlights.json --output-dir highlight-clips --reencode
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Using As A Codex Skill

Install or copy this directory into your Codex skills directory, then invoke it
for requests such as:

- "Find the best clips from this interview."
- "Create highlight shorts from this lecture and transcript."
- "Validate this highlight manifest and export the clips."

Codex should follow `SKILL.md`: inspect the media, inspect the timestamped
transcript, produce a structured manifest, validate it, run a dry export, and
only then export clips.

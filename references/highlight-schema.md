# Highlight Manifest Schema

Use this JSON format for `auto-highlight-video` decisions. The manifest is the contract between AI editorial analysis and local `ffmpeg` export.

## Required Shape

```json
{
  "version": 1,
  "source": {
    "video": "course-session-01.mp4",
    "transcript": "course-session-01.transcript.json"
  },
  "highlights": [
    {
      "id": "clip-01",
      "title": "Why latency budgets change architecture",
      "start": "00:03:12.000",
      "end": "00:04:18.500",
      "score": 8,
      "reason": "The speaker gives a complete explanation with a clear problem, tradeoff, and takeaway.",
      "risk": "Low risk. The clip is self-contained and does not change the speaker's meaning.",
      "edit_notes": "Start after the breath before the question. End after the final sentence about setting budgets."
    },
    {
      "id": "clip-02",
      "title": "The simplest way to explain backpressure",
      "start": "00:08:40.000",
      "end": "00:09:45.000",
      "score": 9,
      "reason": "The analogy is memorable, understandable without prior context, and suitable for a short educational clip.",
      "risk": "Low risk. The analogy stands alone.",
      "edit_notes": "Keep the first sentence because it frames the analogy. Cut before the next topic begins."
    }
  ]
}
```

## Fields

- `version`: Schema version. Use `1`.
- `source.video`: Original video path or filename.
- `source.transcript`: Transcript path or filename used for analysis.
- `highlights`: Ordered list of clips to export.
- `id`: Stable lowercase identifier. Use values like `clip-01`.
- `title`: Human-readable title for review and exported filenames.
- `start`: Clip start time as seconds or `HH:MM:SS.mmm`.
- `end`: Clip end time as seconds or `HH:MM:SS.mmm`.
- `score`: Integer or decimal from 1 to 10.
- `reason`: Why this moment deserves extraction.
- `risk`: Editorial, privacy, copyright, or context risks.
- `edit_notes`: Practical cut notes, such as sentence boundaries or whether to re-encode.

## Constraints

- Keep default durations between 30 and 90 seconds.
- Avoid overlapping clips unless the user explicitly asks for overlapping alternatives.
- Prefer clips scoring 7 or higher for export.
- Do not use precise timecodes from untimestamped transcripts.
- Validate with `python3 scripts/validate_highlights.py <manifest.json>` before exporting.

# Quality Review

Use this reference after media verification and before treating highlight clips as final deliverables.

## Visual Review

- Inspect a contact sheet or representative frames from every clip.
- Check visual consistency across the batch: aspect ratio, framing, subtitles, watermark placement, color, and speaker visibility.
- For short-video delivery, verify landscape, vertical, crop, or reframing choices match the target platform.
- Do not mix burned subtitles and no-subtitle clips unless the user explicitly requested mixed output.

`scripts/analyze_visual_signals.py` can generate representative frame extraction commands and `blackdetect` scan commands for every manifest clip. Use the report as review evidence; do not treat it as a replacement for editorial judgment or transcript-based cut selection.

## Compilation Review

Use `scripts/export_compilation.py --dry-run` before creating a compilation. Confirm the clip order, concat list, output filename, and whether stream copy or re-encoding is appropriate.

After export, verify the compilation has expected duration, video and audio streams, and a natural ending. If clips have mismatched codecs or dimensions, re-encode the compilation instead of relying on stream copy.

## Editorial Review

- Confirm each clip has a hook, a complete idea, and a natural ending.
- Check that the cut does not change the speaker's meaning.
- Remove weak or repetitive clips instead of padding to hit a requested count.
- Prefer fewer strong clips over a full set of mediocre clips.

## Subtitle Policy

Choose one policy for the batch:

- Clean video only.
- Burned subtitles on every clip.
- Separate subtitle files plus clean video.

If subtitles are used, verify they are readable, synchronized, and do not cover key faces, slides, or lower-third text.

## Human Review Gate

Ask for human review when quality depends on taste or context:

- Whether a highlight is actually compelling.
- Whether the clip is culturally or platform appropriate.
- Whether the speaker is represented fairly.
- Whether titles, captions, or vertical framing match the user's publishing goals.

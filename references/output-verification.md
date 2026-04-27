# Output Verification

Use this reference after exporting clips. Command success is not enough; verify the media artifacts.

## Required Checks

1. Expected file count equals the number of manifest highlights.
2. `ffprobe` can read each clip.
3. Each clip has at least one video stream and one audio stream unless the user explicitly asked for silent clips.
4. Duration is within an acceptable tolerance of the manifest range.
5. Codec/container choices match the delivery goal.
6. Full decode passes without errors.

Useful commands:

```bash
ffprobe -v error -show_streams -show_format -of json highlight-clips/clip.mp4
ffmpeg -v error -i highlight-clips/clip.mp4 -f null -
```

For batches, summarize each file as path, duration, video codec/resolution, audio codec, and decode status.

## Compatibility

Stream copy is fast and useful for drafts, but it inherits the source codecs and keyframe boundaries. Re-encode when frame accuracy, platform upload compatibility, or broad playback matters.

For deliverable MP4 clips, prefer:

- Video: H.264 (`libx264`)
- Audio: AAC
- Container: MP4

If the downloaded source uses VP9, AV1, Opus, or another less portable combination, re-encode before treating clips as deliverable.

## Reporting Pattern

Report evidence compactly:

```text
Verified:
- manifest validation: OK: 8 highlight(s)
- exported files: 8 MP4 files
- ffprobe: each file has video and audio streams
- ffmpeg decode: all clips decoded with no errors
```

If a check fails, report the failing clip id or path, the command, and a short stderr summary before retrying only the affected clip.

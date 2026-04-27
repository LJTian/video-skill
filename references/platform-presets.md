# Platform Presets

Use this reference when the user wants social-platform-ready output, captions, titles, summaries, or a specific aspect ratio.

## Ask Or Infer

Clarify production requirements when they affect export choices:

- Keep landscape 16:9 or create vertical 9:16 cuts.
- Burn in subtitles or keep clean video.
- Generate titles, captions, descriptions, or summaries.
- Include or avoid intro, outro, and surrounding context.
- Optimize for Shorts, TikTok, Reels, Bilibili, WeChat Channels, or internal review.

## Practical Defaults

- Internal review: landscape, source resolution or 720p cap, no burned subtitles unless requested.
- Broad upload compatibility: MP4 with H.264 video and AAC audio.
- Vertical short video: reframe or crop deliberately; do not blindly center-crop if slides, faces, or screen recordings matter.
- Burned subtitles: use cleaned timestamped captions and verify text does not cover key visuals.

## Local Rendering

Use `scripts/render_platform_clips.py` after the base clips are exported and reviewed. Start with `--dry-run` so the generated `ffmpeg` commands can be inspected before writing files.

Supported aspect presets:

- `vertical` or `9:16`: 1080x1920.
- `square` or `1:1`: 1080x1080.
- `landscape` or `16:9`: 1920x1080.

The renderer always re-encodes to H.264 video plus AAC audio for upload compatibility. If `--subtitles` is provided, subtitles are burned into every rendered clip.

## Editorial Metadata

For each exported clip, consider producing:

- A concise title.
- A one- or two-sentence description.
- Platform caption copy.
- Hashtag suggestions only when the user wants public social publishing.

Keep metadata separate from the highlight manifest unless it directly affects the cut.

Use `scripts/generate_publish_assets.py` to create reviewable titles, descriptions, captions, hashtags, cover suggestions, and manual review items. The script does not upload, schedule, or call platform APIs.

# Source Acquisition

Use this reference when the user provides a URL, especially YouTube, instead of a local media file.

## Probe Before Download

Check tools first:

```bash
yt-dlp --version
ffmpeg -version
ffprobe -version
```

Avoid downloading a large video until the transcript and manifest path is viable:

1. Dump metadata or list subtitles with `yt-dlp --skip-download --list-subs <url>`.
2. Download timestamped subtitles first with `--write-subs` or `--write-auto-subs`.
3. Clean and inspect a sample before trusting auto-captions.
4. Build and validate the highlight manifest.
5. Download the source video after the manifest is viable.

For review workflows, cap the default download to a reasonable edit copy unless the user requests higher quality:

```bash
yt-dlp -f "bv*[height<=720]+ba/b[height<=720]/b" <url>
```

## Subtitle Fallbacks

Prefer timestamped `vtt`, `srt`, or `json3`. If the preferred language fails but another timestamped language is available, proceed only when that language is adequate for editorial judgment. Do not fabricate timestamps or translate untimestamped text into precise cut points.

For WebVTT auto-captions, use:

```bash
python3 scripts/clean_vtt.py captions.vtt -o captions.clean.txt
```

## YouTube Auth And Bot Blocks

When metadata or subtitle access is blocked:

1. Try `yt-dlp --cookies-from-browser <browser>`.
2. If browser cookies cannot be decrypted, ask the user for a Netscape-format `cookies.txt`.
3. Use the cookie file only for the download command that needs it.

Never print cookie contents. Mention `cookies.txt` cleanup in the final response when it was used. Do not include cookies, browser profiles, auth headers, tokens, or private files in manifests or output bundles.

## Failure Branches

- No timestamped subtitles: generate a timestamped transcript before selecting highlights.
- Poor subtitle quality: inspect samples and report uncertainty before relying on it.
- Subtitle HTTP 429: use another adequate timestamped language or retry later.
- Download blocked: request `cookies.txt` or a local video file.

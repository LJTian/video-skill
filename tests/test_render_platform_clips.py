import unittest
from pathlib import Path

from scripts.render_platform_clips import build_output_path, build_platform_command, build_video_filter


class RenderPlatformClipsTests(unittest.TestCase):
    def test_build_video_filter_supports_vertical_with_subtitles(self):
        video_filter = build_video_filter("9:16", subtitles=Path("captions.srt"))

        self.assertEqual(
            video_filter,
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles=captions.srt",
        )

    def test_build_video_filter_rejects_unknown_aspect(self):
        with self.assertRaises(ValueError):
            build_video_filter("4:3")

    def test_build_output_path_includes_profile(self):
        clip = {"id": "clip-01", "title": "Why Latency Matters"}

        path = build_output_path(Path("out"), clip, "vertical")

        self.assertEqual(path, Path("out/clip-01-why-latency-matters-vertical.mp4"))

    def test_build_platform_command_reencodes_for_upload_compatibility(self):
        command = build_platform_command(
            Path("clips/clip-01.mp4"),
            Path("out/clip-01-vertical.mp4"),
            aspect="vertical",
            subtitles=Path("captions.srt"),
        )

        self.assertEqual(command[:4], ["ffmpeg", "-y", "-i", "clips/clip-01.mp4"])
        video_filter = command[command.index("-vf") + 1]
        self.assertIn("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", video_filter)
        self.assertIn("subtitles=captions.srt", video_filter)
        self.assertIn("libx264", command)
        self.assertIn("aac", command)
        self.assertEqual(command[-1], "out/clip-01-vertical.mp4")


if __name__ == "__main__":
    unittest.main()

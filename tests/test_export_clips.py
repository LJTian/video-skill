import unittest
from pathlib import Path

from scripts.export_clips import build_ffmpeg_command, build_output_path, safe_slug


class ExportClipsTests(unittest.TestCase):
    def test_safe_slug_removes_unsafe_characters(self):
        self.assertEqual(safe_slug("Why latency: budgets matter?!"), "why-latency-budgets-matter")
        self.assertEqual(safe_slug("  ---  "), "clip")

    def test_build_output_path_uses_id_and_title(self):
        clip = {"id": "clip-01", "title": "Why Latency Matters"}

        path = build_output_path(Path("out"), clip)

        self.assertEqual(path, Path("out/clip-01-why-latency-matters.mp4"))

    def test_build_ffmpeg_command_defaults_to_stream_copy(self):
        clip = {
            "id": "clip-01",
            "title": "Latency",
            "start_seconds": 65.0,
            "end_seconds": 130.5,
        }

        command = build_ffmpeg_command(Path("talk.mp4"), Path("out/clip.mp4"), clip)

        self.assertEqual(
            command,
            [
                "ffmpeg",
                "-y",
                "-ss",
                "65.000",
                "-i",
                "talk.mp4",
                "-t",
                "65.500",
                "-map",
                "0",
                "-c",
                "copy",
                "out/clip.mp4",
            ],
        )

    def test_build_ffmpeg_command_supports_reencode(self):
        clip = {
            "id": "clip-01",
            "title": "Latency",
            "start_seconds": 65.0,
            "end_seconds": 130.5,
        }

        command = build_ffmpeg_command(Path("talk.mp4"), Path("out/clip.mp4"), clip, reencode=True)

        self.assertIn("-c:v", command)
        self.assertIn("libx264", command)
        self.assertIn("-c:a", command)
        self.assertIn("aac", command)
        self.assertNotIn("copy", command)


if __name__ == "__main__":
    unittest.main()

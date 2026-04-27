import unittest
from pathlib import Path

from scripts.export_compilation import build_compilation_command, build_concat_lines, sort_clips


class ExportCompilationTests(unittest.TestCase):
    def test_sort_clips_preserves_manifest_order_by_default(self):
        clips = [
            {"id": "clip-01", "title": "First", "score": 7},
            {"id": "clip-02", "title": "Second", "score": 9},
        ]

        self.assertEqual([clip["id"] for clip in sort_clips(clips, order="manifest")], ["clip-01", "clip-02"])

    def test_sort_clips_can_order_by_score_descending(self):
        clips = [
            {"id": "clip-01", "title": "First", "score": 7},
            {"id": "clip-02", "title": "Second", "score": 9},
        ]

        self.assertEqual([clip["id"] for clip in sort_clips(clips, order="score")], ["clip-02", "clip-01"])

    def test_build_concat_lines_uses_exported_clip_filenames(self):
        clips = [
            {"id": "clip-01", "title": "Why Latency Matters"},
            {"id": "clip-02", "title": "Backpressure Basics"},
        ]

        lines = build_concat_lines(clips, Path("highlight-clips"))

        self.assertEqual(
            lines,
            [
                "file 'highlight-clips/clip-01-why-latency-matters.mp4'",
                "file 'highlight-clips/clip-02-backpressure-basics.mp4'",
            ],
        )

    def test_build_compilation_command_uses_concat_demuxer(self):
        command = build_compilation_command(Path("out/concat.txt"), Path("out/compilation.mp4"))

        self.assertEqual(
            command,
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                "out/concat.txt",
                "-c",
                "copy",
                "out/compilation.mp4",
            ],
        )


if __name__ == "__main__":
    unittest.main()

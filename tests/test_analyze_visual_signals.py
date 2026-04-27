import unittest
from pathlib import Path

from scripts.analyze_visual_signals import build_blackdetect_command, build_frame_commands, sample_times


class AnalyzeVisualSignalsTests(unittest.TestCase):
    def test_sample_times_include_start_middle_and_near_end(self):
        clip = {"id": "clip-01", "start_seconds": 10.0, "end_seconds": 40.0}

        self.assertEqual(sample_times(clip, samples=3), [10.0, 25.0, 39.999])

    def test_build_frame_commands_extract_representative_frames(self):
        clip = {"id": "clip-01", "title": "Latency", "start_seconds": 10.0, "end_seconds": 40.0}

        commands = build_frame_commands(Path("talk.mp4"), clip, Path("frames"), samples=2)

        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0][:4], ["ffmpeg", "-y", "-ss", "10.000"])
        self.assertIn("talk.mp4", commands[0])
        self.assertEqual(commands[0][-1], "frames/clip-01-001.jpg")
        self.assertEqual(commands[1][-1], "frames/clip-01-002.jpg")

    def test_build_blackdetect_command_limits_scan_to_clip_range(self):
        clip = {"id": "clip-01", "start_seconds": 10.0, "end_seconds": 40.0}

        command = build_blackdetect_command(Path("talk.mp4"), clip)

        self.assertEqual(
            command,
            [
                "ffmpeg",
                "-ss",
                "10.000",
                "-i",
                "talk.mp4",
                "-t",
                "30.000",
                "-vf",
                "blackdetect=d=0.5:pix_th=0.10",
                "-an",
                "-f",
                "null",
                "-",
            ],
        )


if __name__ == "__main__":
    unittest.main()

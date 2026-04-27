import unittest

from scripts.review_clip_boundaries import parse_vtt_cues, review_clip_boundaries


class ReviewClipBoundariesTests(unittest.TestCase):
    def test_parse_vtt_cues_removes_inline_markup(self):
        raw = """WEBVTT

00:00:01.000 --> 00:00:03.500
<c>Hello</c> <00:00:02.000>world
"""

        cues = parse_vtt_cues(raw)

        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0].start_seconds, 1.0)
        self.assertEqual(cues[0].end_seconds, 3.5)
        self.assertEqual(cues[0].text, "Hello world")

    def test_reports_end_cut_inside_transcript_cue(self):
        payload = {
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Incomplete ending",
                    "start": "00:00:10.000",
                    "end": "00:00:40.000",
                    "score": 8,
                    "reason": "A useful point.",
                    "risk": "Low.",
                    "edit_notes": "End after the sentence.",
                }
            ]
        }
        transcript = """WEBVTT

00:00:38.000 --> 00:00:42.000
This sentence is still being spoken.
"""

        issues = review_clip_boundaries(payload, transcript, tail_padding=0.5)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["clip_id"], "clip-01")
        self.assertEqual(issues[0]["boundary"], "end")
        self.assertEqual(issues[0]["issue"], "cuts_inside_transcript_cue")
        self.assertEqual(issues[0]["suggested_time"], "00:00:42.500")
        self.assertIn("still being spoken", issues[0]["cue_text"])

    def test_reports_start_cut_inside_transcript_cue(self):
        payload = {
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Incomplete start",
                    "start": "00:00:10.000",
                    "end": "00:00:45.000",
                    "score": 8,
                    "reason": "A useful point.",
                    "risk": "Low.",
                    "edit_notes": "Start at the sentence.",
                }
            ]
        }
        transcript = """WEBVTT

00:00:08.000 --> 00:00:12.000
The sentence began before this clip.
"""

        issues = review_clip_boundaries(payload, transcript, lead_padding=0.25)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["boundary"], "start")
        self.assertEqual(issues[0]["suggested_time"], "00:00:07.750")

    def test_boundary_on_cue_edge_is_clean(self):
        payload = {
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Clean boundary",
                    "start": "00:00:10.000",
                    "end": "00:00:40.000",
                    "score": 8,
                    "reason": "A useful point.",
                    "risk": "Low.",
                    "edit_notes": "Clean boundaries.",
                }
            ]
        }
        transcript = """WEBVTT

00:00:40.000 --> 00:00:42.000
The next sentence begins after the cut.
"""

        issues = review_clip_boundaries(payload, transcript)

        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()

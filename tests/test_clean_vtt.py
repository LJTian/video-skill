import unittest

from scripts.clean_vtt import clean_vtt_text


class CleanVttTests(unittest.TestCase):
    def test_removes_webvtt_markup_inline_timing_and_rolling_duplicates(self):
        raw = """WEBVTT

00:00:01.000 --> 00:00:03.000
<c>hello</c> <00:00:01.500>world

00:00:03.000 --> 00:00:05.000
<c>hello</c> <00:00:03.500>world

00:00:05.000 --> 00:00:08.000
The &amp; operator matters.
"""

        lines = clean_vtt_text(raw)

        self.assertEqual(
            lines,
            [
                "[00:00:01.000 --> 00:00:03.000] hello world",
                "[00:00:05.000 --> 00:00:08.000] The & operator matters.",
            ],
        )


if __name__ == "__main__":
    unittest.main()

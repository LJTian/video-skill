import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.validate_highlights import ValidationError, load_highlights, validate_highlights


def write_json(payload):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    with tmp:
        json.dump(payload, tmp)
    return Path(tmp.name)


class ValidateHighlightsTests(unittest.TestCase):
    def test_accepts_valid_highlight_list(self):
        payload = {
            "version": 1,
            "source": {"video": "talk.mp4", "transcript": "talk.json"},
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Why latency budgets matter",
                    "start": "00:01:05.000",
                    "end": "00:02:10.500",
                    "score": 8,
                    "reason": "Clear standalone explanation with a strong takeaway.",
                    "risk": "Low risk.",
                    "edit_notes": "Cut after the speaker finishes the sentence.",
                }
            ],
        }

        highlights = validate_highlights(payload)

        self.assertEqual(len(highlights), 1)
        self.assertEqual(highlights[0]["start_seconds"], 65.0)
        self.assertEqual(highlights[0]["end_seconds"], 130.5)

    def test_rejects_missing_required_field(self):
        payload = {
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Incomplete",
                    "start": "00:00:10",
                    "end": "00:01:00",
                    "score": 7,
                }
            ]
        }

        with self.assertRaisesRegex(ValidationError, "reason"):
            validate_highlights(payload)

    def test_rejects_duplicate_ids(self):
        clip = {
            "id": "clip-01",
            "title": "Duplicate",
            "start": "00:00:10",
            "end": "00:01:00",
            "score": 7,
            "reason": "Strong moment.",
            "risk": "Low.",
            "edit_notes": "Use clean cut.",
        }
        payload = {"highlights": [clip, {**clip, "start": "00:02:00", "end": "00:03:00"}]}

        with self.assertRaisesRegex(ValidationError, "Duplicate id"):
            validate_highlights(payload)

    def test_rejects_duration_outside_default_bounds(self):
        payload = {
            "highlights": [
                {
                    "id": "clip-01",
                    "title": "Too short",
                    "start": 10,
                    "end": 20,
                    "score": 8,
                    "reason": "Short moment.",
                    "risk": "Low.",
                    "edit_notes": "Use clean cut.",
                }
            ]
        }

        with self.assertRaisesRegex(ValidationError, "duration"):
            validate_highlights(payload)

    def test_rejects_overlapping_clips(self):
        base = {
            "title": "Overlap",
            "score": 8,
            "reason": "Strong moment.",
            "risk": "Low.",
            "edit_notes": "Use clean cut.",
        }
        payload = {
            "highlights": [
                {**base, "id": "clip-01", "start": "00:00:10", "end": "00:01:10"},
                {**base, "id": "clip-02", "start": "00:01:00", "end": "00:02:00"},
            ]
        }

        with self.assertRaisesRegex(ValidationError, "overlap"):
            validate_highlights(payload)

    def test_loads_json_file(self):
        path = write_json({"highlights": []})
        self.addCleanup(path.unlink)

        self.assertEqual(load_highlights(path), {"highlights": []})

    def test_schema_reference_example_is_valid(self):
        schema_path = Path("references/highlight-schema.md")
        text = schema_path.read_text(encoding="utf-8")
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        self.assertIsNotNone(match, "schema reference must include a JSON example")
        payload = json.loads(match.group(1))

        highlights = validate_highlights(payload)

        self.assertGreaterEqual(len(highlights), 1)


if __name__ == "__main__":
    unittest.main()

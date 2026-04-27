import re
import unittest
from pathlib import Path


class SkillDocsTests(unittest.TestCase):
    def test_skill_frontmatter_and_ordering_are_present(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: auto-highlight-video", text)
        self.assertRegex(text, r"description: .+高光|description: .+highlight")
        validate_index = text.index("validate_highlights.py")
        boundary_index = text.index("review_clip_boundaries.py")
        export_index = text.index("export_clips.py")
        self.assertLess(validate_index, export_index)
        self.assertLess(boundary_index, export_index)

    def test_skill_links_to_schema_reference(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(re.search(r"references/highlight-schema\.md", text))

    def test_skill_covers_url_acquisition_and_post_export_verification(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        for required in (
            "references/source-acquisition.md",
            "references/output-verification.md",
            "references/platform-presets.md",
            "yt-dlp",
            "cookies.txt",
            "ffmpeg -v error",
            "Credential Safety",
        ):
            self.assertIn(required, text)

        source_index = text.index("Acquire source")
        transcript_index = text.index("Inspect the transcript")
        verify_index = text.index("Verify exported media")
        export_index = text.index("Export clips")
        self.assertLess(source_index, transcript_index)
        self.assertGreater(verify_index, export_index)

    def test_references_exist_for_real_world_video_workflows(self):
        for path in (
            Path("references/source-acquisition.md"),
            Path("references/output-verification.md"),
            Path("references/platform-presets.md"),
            Path("references/quality-review.md"),
        ):
            self.assertTrue(path.exists(), f"missing reference: {path}")

    def test_skill_requires_production_quality_review(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        for required in (
            "references/quality-review.md",
            "Review production quality",
            "contact sheet",
            "subtitle policy",
            "visual consistency",
            "human review",
        ):
            self.assertIn(required, text)

        verify_index = text.index("Verify exported media")
        quality_index = text.index("Review production quality")
        self.assertGreater(quality_index, verify_index)

    def test_skill_requires_transcript_boundary_review_before_export(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        for required in (
            "review_clip_boundaries.py",
            "transcript cue",
            "sentence boundaries",
        ):
            self.assertIn(required, text)

        boundary_index = text.index("Review clip boundaries")
        export_index = text.index("Export clips")
        self.assertLess(boundary_index, export_index)


if __name__ == "__main__":
    unittest.main()

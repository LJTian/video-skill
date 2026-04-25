import re
import unittest
from pathlib import Path


class SkillDocsTests(unittest.TestCase):
    def test_skill_frontmatter_and_ordering_are_present(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: auto-highlight-video", text)
        self.assertRegex(text, r"description: .+高光|description: .+highlight")
        validate_index = text.index("validate_highlights.py")
        export_index = text.index("export_clips.py")
        self.assertLess(validate_index, export_index)

    def test_skill_links_to_schema_reference(self):
        text = Path("SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(re.search(r"references/highlight-schema\.md", text))


if __name__ == "__main__":
    unittest.main()

import unittest

from scripts.generate_publish_assets import build_publish_asset, suggest_hashtags


class GeneratePublishAssetsTests(unittest.TestCase):
    def test_suggest_hashtags_uses_title_keywords(self):
        tags = suggest_hashtags("Why Latency Budgets Matter", platform="Shorts")

        self.assertEqual(tags, ["#latency", "#budgets", "#matter", "#shorts"])

    def test_build_publish_asset_preserves_editorial_risk_for_review(self):
        clip = {
            "id": "clip-01",
            "title": "Why Latency Budgets Matter",
            "reason": "The speaker explains a complete tradeoff with a clear takeaway.",
            "risk": "Low risk. Self-contained.",
            "edit_notes": "Start after the setup sentence.",
        }

        asset = build_publish_asset(clip, platform="Shorts", audience="backend engineers")

        self.assertEqual(asset["id"], "clip-01")
        self.assertEqual(asset["platform"], "Shorts")
        self.assertEqual(asset["title"], "Why Latency Budgets Matter")
        self.assertIn("backend engineers", asset["description"])
        self.assertIn("clear takeaway", asset["caption"])
        self.assertEqual(asset["hashtags"], ["#latency", "#budgets", "#matter", "#shorts"])
        self.assertIn("Review editorial risk: Low risk. Self-contained.", asset["review_items"])


if __name__ == "__main__":
    unittest.main()

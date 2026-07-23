import unittest

from core.action_signal import resolve_action_signal


class ActionSignalTests(unittest.TestCase):
    def test_short_english_keyword_requires_token_boundaries(self):
        self.assertIsNone(resolve_action_signal("Ada is now using the reusable adapter."))
        action = resolve_action_signal("No, that is not the requested behavior.")
        self.assertIsNotNone(action)
        self.assertEqual(action["behavior"], "reject")
        self.assertIn("no", action["matchedKeywords"])

    def test_cjk_phrase_keeps_substring_matching(self):
        action = resolve_action_signal("例如，角色可以自然地解释这个功能。")
        self.assertIsNotNone(action)
        self.assertEqual(action["behavior"], "explain")


if __name__ == "__main__":
    unittest.main()

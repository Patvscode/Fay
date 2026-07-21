import unittest

from core.avatar_action import (
    ALLOWED_BEHAVIORS,
    build_avatar_action_message,
    normalize_avatar_action,
)


class AvatarActionTests(unittest.TestCase):
    def test_all_reviewed_behaviors_build_action_only_messages(self):
        for behavior in ALLOWED_BEHAVIORS:
            message = build_avatar_action_message(behavior, 0.75, 2.5)
            self.assertEqual(message["Data"]["Key"], "action")
            self.assertEqual(message["Data"]["Action"]["behavior"], behavior)
            self.assertNotIn("HttpValue", message["Data"])

    def test_normalization_is_bounded_and_case_insensitive(self):
        action = normalize_avatar_action(" WAVE ", 0.0, 0.2)
        self.assertEqual(action["behavior"], "wave")
        self.assertEqual(action["intensity"], 0.0)

    def test_unknown_behavior_and_non_finite_values_fail_closed(self):
        for args in (("dance", 0.5, 1.0), ("wave", float("nan"), 1.0), ("wave", 0.5, 20.0)):
            with self.assertRaises(ValueError):
                normalize_avatar_action(*args)


if __name__ == "__main__":
    unittest.main()

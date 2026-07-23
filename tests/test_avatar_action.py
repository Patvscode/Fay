import unittest

from core.avatar_action import (
    ALLOWED_BEHAVIORS,
    ALLOWED_MOTION_PROVIDERS,
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

    def test_provider_hint_is_bounded_and_carried_to_the_renderer(self):
        for provider in ALLOWED_MOTION_PROVIDERS:
            action = normalize_avatar_action("wave", provider=provider)
            self.assertEqual(action["provider"], provider)
            message = build_avatar_action_message("wave", provider=provider)
            self.assertEqual(message["Data"]["Action"]["provider"], provider)

        for provider in ("ardy", "auto", "", 1, False):
            with self.assertRaisesRegex(ValueError, "provider"):
                normalize_avatar_action("wave", provider=provider)

    def test_missing_provider_preserves_legacy_hybrid_wire_contract(self):
        action = normalize_avatar_action("wave")
        message = build_avatar_action_message("wave")
        self.assertNotIn("provider", action)
        self.assertNotIn("provider", message["Data"]["Action"])

    def test_free_text_motion_prompt_is_carried_without_term_classification(self):
        prompt = "Crouch, take two careful steps, then wave with your left hand."
        action = normalize_avatar_action("explain", prompt=prompt)
        message = build_avatar_action_message("explain", prompt=prompt)
        self.assertEqual(action["prompt"], prompt)
        self.assertEqual(message["Data"]["Action"]["prompt"], prompt)

        for invalid in ("", " ", 42, "x" * 513):
            with self.assertRaisesRegex(ValueError, "prompt"):
                normalize_avatar_action("explain", prompt=invalid)


if __name__ == "__main__":
    unittest.main()

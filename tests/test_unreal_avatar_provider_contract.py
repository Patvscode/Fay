import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "avatar/unreal/FayAvatarRuntime/Plugins/FayAvatarBridge/Source/FayAvatarBridge"


class UnrealAvatarProviderContractTests(unittest.TestCase):
    def test_http_and_mcp_boundaries_carry_only_the_two_provider_values(self):
        flask_server = (ROOT / "gui/flask_server.py").read_text()
        mcp_server = (ROOT / "faymcp/mcp_server.py").read_text()
        self.assertIn("data.get('provider')", flask_server)
        self.assertIn('"enum": ["baked", "hybrid"]', mcp_server)
        self.assertIn('provider not in {"baked", "hybrid"}', mcp_server)
        self.assertIn('payload["provider"] = provider', mcp_server)

    def test_bundled_bridge_carries_the_bounded_provider_hint(self):
        header = (PLUGIN / "Public/FayAvatarBridgeComponent.h").read_text()
        source = (PLUGIN / "Private/FayAvatarBridgeComponent.cpp").read_text()
        self.assertIn("FString Provider;", header)
        self.assertIn('(Key != TEXT("audio") && Key != TEXT("action"))', source)
        self.assertIn('Action->HasField(TEXT("provider"))', source)
        self.assertIn('OutMessage.Action.Provider != TEXT("baked")', source)
        self.assertIn('OutMessage.Action.Provider != TEXT("hybrid")', source)
        self.assertIn('if (Key == TEXT("action"))', source)


if __name__ == "__main__":
    unittest.main()

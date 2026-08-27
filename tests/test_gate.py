# tests/test_gate.py
import unittest
from unittest.mock import patch
import sys

from mynah.tools.base import ToolRegistry
import mynah.safety.gate as gate
from run import setup_registry

class TestSafetyGate(unittest.TestCase):
    def setUp(self):
        self.registry = setup_registry()

    def test_registry_enforces_risk(self):
        """Verifies that ToolRegistry raises ValueError if registered without risk or invalid risk."""
        r = ToolRegistry()
        # Should raise ValueError
        with self.assertRaises(ValueError):
            r.register("test.tool", "description", "invalid-risk", lambda: None)
            
        with self.assertRaises(ValueError):
            # Missing risk / None
            r.register("test.tool", "description", None, lambda: None)

    def test_all_registered_tools_have_risk(self):
        """Verifies that every tool in our default setup has a risk classification."""
        for name, info in self.registry.registry.items():
            self.assertIn(info["risk"], ("safe", "irreversible"), f"Tool '{name}' lacks valid risk classification.")

    def test_safe_tool_bypasses_gate(self):
        """Verifies that safe tools return True automatically from safety gate check."""
        # apps.launch is marked as 'safe'
        self.assertTrue(gate.check(self.registry, "apps.launch", {"name": "Calculator"}))

    @patch("mynah.safety.gate.wait_for_confirmation")
    def test_irreversible_tool_requires_confirmation_yes(self, mock_confirm):
        """Verifies that irreversible tools are approved if wait_for_confirmation returns True."""
        mock_confirm.return_value = True
        # systems.delete_file is marked as 'irreversible'
        res = gate.check(self.registry, "systems.delete_file", {"path": "/tmp/test.txt"})
        self.assertTrue(res)
        mock_confirm.assert_called_once()

    @patch("mynah.safety.gate.wait_for_confirmation")
    def test_irreversible_tool_requires_confirmation_no(self, mock_confirm):
        """Verifies that irreversible tools are blocked if wait_for_confirmation returns False."""
        mock_confirm.return_value = False
        res = gate.check(self.registry, "systems.delete_file", {"path": "/tmp/test.txt"})
        self.assertFalse(res)
        mock_confirm.assert_called_once()

if __name__ == "__main__":
    unittest.main()

# tests/test_router.py
import unittest
import os
import shutil
import tempfile
import yaml

from mynah.router.rules import RuleRouter
from mynah.tools.base import ToolRegistry

class TestRuleRouter(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for testing rules
        self.test_dir = tempfile.mkdtemp()
        self.rules_file = os.path.join(self.test_dir, "instant.yaml")
        
        # Write mock rules to temp file
        self.mock_rules = [
            {"pattern": "open (.+)", "tool": "apps.launch", "args": {"name": "$1"}},
            {"pattern": "quit (.+)", "tool": "apps.quit", "args": {"name": "$1"}},
            {"pattern": "volume (\\d+)", "tool": "windows.set_volume", "args": {"level": "$1"}},
            {"pattern": "mute", "tool": "windows.mute", "args": {}},
            {"pattern": "remember that (.+)", "tool": "vault.append", "args": {"text": "$1"}}
        ]
        with open(self.rules_file, "w") as f:
            yaml.safe_dump(self.mock_rules, f)
            
        self.router = RuleRouter(self.rules_file)

    def tearDown(self):
        # Clean up temp files
        shutil.rmtree(self.test_dir)

    def test_load_rules(self):
        self.assertEqual(len(self.router.rules), 5)
        self.assertEqual(self.router.rules[0]["tool"], "apps.launch")

    def test_routing_app_launch(self):
        res = self.router.route("open Safari")
        self.assertIsNotNone(res)
        self.assertEqual(res["tool"], "apps.launch")
        self.assertEqual(res["args"], {"name": "Safari"})

    def test_routing_volume(self):
        res = self.router.route("volume 50")
        self.assertIsNotNone(res)
        self.assertEqual(res["tool"], "windows.set_volume")
        self.assertEqual(res["args"], {"level": "50"})

    def test_routing_mute(self):
        res = self.router.route("mute")
        self.assertIsNotNone(res)
        self.assertEqual(res["tool"], "windows.mute")
        self.assertEqual(res["args"], {})

    def test_routing_no_match(self):
        res = self.router.route("what is my name")
        self.assertIsNone(res)

class TestToolRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        
    def test_register_and_execute(self):
        def mock_func(x, y):
            return x + y
            
        self.registry.register("math.add", "Adds two numbers", "safe", mock_func)
        self.assertIn("math.add", self.registry.registry)
        
        result = self.registry.execute("math.add", {"x": 5, "y": 10})
        self.assertEqual(result, 15)

    def test_execute_unregistered(self):
        with self.assertRaises(KeyError):
            self.registry.execute("nonexistent.tool", {})

if __name__ == "__main__":
    unittest.main()

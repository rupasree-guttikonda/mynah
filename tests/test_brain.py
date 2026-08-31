# tests/test_brain.py
import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import tempfile

import mynah.router.brain as brain
from mynah.tools.base import ToolRegistry
from mynah.memory.context import count_tokens, get_profile_context, get_recent_history
from mynah.log.metrics import check_daily_budget, count_tokens as metrics_count_tokens
from mynah.router.benchmark import benchmark_ollama

class TestBrainRouter(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        # Register a safe tool
        self.registry.register(
            "test.safe_tool", 
            "Test description", 
            "safe", 
            lambda x: f"Safe {x}",
            {
                "type": "object",
                "properties": {
                    "x": {"type": "string"}
                },
                "required": ["x"]
            }
        )

    def test_build_openai_tools(self):
        tools = brain.build_openai_tools(self.registry)
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["type"], "function")
        self.assertEqual(tools[0]["function"]["name"], "test.safe_tool")
        self.assertEqual(tools[0]["function"]["parameters"]["required"], ["x"])

    def test_assess_confidence_success(self):
        res = {"type": "tool", "tool": "test.safe_tool", "args": {"x": "hello"}}
        self.assertTrue(brain.assess_confidence(res, self.registry))

    def test_assess_confidence_failures(self):
        # 1. Incorrect type
        res = {"type": "tool", "tool": "test.safe_tool", "args": {"x": 123}} # expects string
        self.assertFalse(brain.assess_confidence(res, self.registry))
        
        # 2. Missing required argument
        res = {"type": "tool", "tool": "test.safe_tool", "args": {}}
        self.assertFalse(brain.assess_confidence(res, self.registry))
        
        # 3. Tool name not registered
        res = {"type": "tool", "tool": "test.unknown_tool", "args": {"x": "hello"}}
        self.assertFalse(brain.assess_confidence(res, self.registry))

    @patch("mynah.router.brain.get_daily_spend")
    @patch("mynah.router.brain.get_cloud_client")
    def test_route_cloud_budget_enforcement(self, mock_client, mock_spend):
        # Set spend above limit ($1.00)
        mock_spend.return_value = 1.05
        
        res = brain.route_cloud_fallback("joke", "context", self.registry)
        self.assertEqual(res["type"], "refusal")
        self.assertIn("Daily spend limit reached", res["content"])
        mock_client.assert_not_called()

    def test_check_daily_budget_helper(self):
        within, cost = check_daily_budget("nonexistent.db", max_usd=1.00)
        self.assertTrue(within)
        self.assertEqual(cost, 0.0)

    def test_benchmark_ollama_structure(self):
        res = benchmark_ollama(model_name="nonexistent-test-model")
        self.assertIn("system_ram_gb", res)
        self.assertIn("latency_sec", res)

class TestContextInjection(unittest.TestCase):
    def setUp(self):
        self.temp_vault = tempfile.mkdtemp()
        import mynah.config as config
        import mynah.memory.context as context
        
        self.original_config_vault = config.VAULT_DIR
        self.original_context_vault = context.VAULT_DIR
        
        config.VAULT_DIR = self.temp_vault
        context.VAULT_DIR = self.temp_vault

    def tearDown(self):
        import mynah.config as config
        import mynah.memory.context as context
        
        config.VAULT_DIR = self.original_config_vault
        context.VAULT_DIR = self.original_context_vault
        shutil.rmtree(self.temp_vault)

    def test_token_counting(self):
        self.assertEqual(count_tokens("hello world"), 2)
        self.assertEqual(metrics_count_tokens("hello world"), 2)

    def test_get_profile_context_capping(self):
        me_dir = os.path.join(self.temp_vault, "me")
        os.makedirs(me_dir, exist_ok=True)
        
        large_text = "word " * 1000
        with open(os.path.join(me_dir, "identity.md"), "w") as f:
            f.write(large_text)
            
        context_str = get_profile_context()
        self.assertIn("[... Context Truncated ...]", context_str)
        self.assertLessEqual(count_tokens(context_str), 520)

if __name__ == "__main__":
    unittest.main()

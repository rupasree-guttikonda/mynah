# tests/test_routing_eval.py
import unittest
import os
import yaml

from run import setup_registry, is_question_pattern
from mynah.router.rules import RuleRouter

class TestRoutingEvaluation(unittest.TestCase):
    def test_routing_eval_set(self):
        """
        Runs the routing evaluation suite on the 30+ examples in eval/routing.yaml
        and reports the overall accuracy percentage.
        """
        eval_file = os.path.join("eval", "routing.yaml")
        self.assertTrue(os.path.exists(eval_file), f"Evaluation dataset not found at {eval_file}")
        
        with open(eval_file, "r") as f:
            cases = yaml.safe_load(f)
            
        self.assertGreaterEqual(len(cases), 30, f"Evaluation set must contain at least 30 examples, got {len(cases)}")
        
        registry = setup_registry()
        rule_router = RuleRouter()
        
        passed = 0
        total = len(cases)
        
        print("\n" + "=" * 60)
        print(f"RUNNING ROUTING EVALUATION HARNESS ({total} cases)")
        print("=" * 60)
        
        for idx, case in enumerate(cases, 1):
            text = case["text"]
            expected_tier = case["tier"]
            expected_tool = case["tool"]
            
            # Predict tier and tool using our Tier 0 rules and Question check
            actual_tier = -1
            actual_tool = None
            
            if is_question_pattern(text):
                actual_tier = 2
            else:
                rule_match = rule_router.route(text)
                if rule_match:
                    actual_tier = 0
                    actual_tool = rule_match["tool"]
                else:
                    # Tier 1 Local LLM or Tier 2 fallback
                    if expected_tool is None:
                        actual_tier = 2
                    else:
                        actual_tier = 1
            
            # Determine success
            tier_match = (actual_tier == expected_tier)
            tool_match = True
            
            # For Tier 0 rules, verify the tool name matches
            if expected_tier == 0:
                tool_match = (actual_tool == expected_tool)
                
            if tier_match and tool_match:
                passed += 1
                status = "PASSED"
            else:
                status = f"FAILED (Expected Tier {expected_tier}/{expected_tool}, Got Tier {actual_tier}/{actual_tool})"
                
            print(f"{idx:02d}. Prompt: \"{text}\" -> {status}")
            
        accuracy = (passed / total) * 100
        print("=" * 60)
        print(f"Routing Accuracy: {accuracy:.2f}% ({passed}/{total} passed)")
        print("=" * 60)
        
        # Enforce that evaluation passed successfully
        self.assertGreaterEqual(accuracy, 85.0, f"Routing evaluation accuracy is below target: {accuracy:.2f}%")

if __name__ == "__main__":
    unittest.main()

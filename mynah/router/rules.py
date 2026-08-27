# mynah/router/rules.py
import re
import yaml
import os

RULES_PATH = "rules/instant.yaml"

class RuleRouter:
    def __init__(self, rules_path: str = RULES_PATH):
        self.rules_path = rules_path
        self.rules = []
        self.load_rules()

    def load_rules(self):
        """Loads and compiles regex rules from rules/instant.yaml."""
        if not os.path.exists(self.rules_path):
            self.rules = []
            return
            
        with open(self.rules_path, "r") as f:
            try:
                raw_rules = yaml.safe_load(f) or []
                for r in raw_rules:
                    pattern_str = r.get("pattern")
                    if pattern_str:
                        # Compile case-insensitive regex
                        compiled_pattern = re.compile(f"^{pattern_str}$", re.IGNORECASE)
                        self.rules.append({
                            "regex": compiled_pattern,
                            "tool": r.get("tool"),
                            "args_template": r.get("args", {})
                        })
            except yaml.YAMLError:
                self.rules = []

    def route(self, text: str) -> dict:
        """
        Routes the transcript text against the compiled patterns.
        Returns a dict with 'tool' and 'args' if matched, or None.
        """
        cleaned_text = text.strip()
        
        for rule in self.rules:
            match = rule["regex"].match(cleaned_text)
            if match:
                # Extract positional match groups (1-indexed)
                groups = match.groups()
                
                # Resolve argument templates (replacing $1, $2, etc. with group values)
                resolved_args = {}
                for key, val in rule["args_template"].items():
                    if isinstance(val, str) and val.startswith("$"):
                        try:
                            group_idx = int(val[1:]) - 1
                            if 0 <= group_idx < len(groups):
                                resolved_args[key] = groups[group_idx]
                            else:
                                resolved_args[key] = ""
                        except ValueError:
                            resolved_args[key] = val
                    else:
                        resolved_args[key] = val
                
                return {
                    "tool": rule["tool"],
                    "args": resolved_args
                }
                
        return None

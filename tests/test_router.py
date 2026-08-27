import yaml
from pathlib import Path

def test_instant_rules_yaml_structure():
    rules_path = Path("rules/instant.yaml")
    assert rules_path.exists(), "instant.yaml should exist"
    with open(rules_path, "r") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, list)
    assert len(data) > 0
    for rule in data:
        assert "pattern" in rule
        assert "tool" in rule

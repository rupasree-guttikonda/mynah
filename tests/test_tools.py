import pytest
from mynah.tools.base import ToolRegistry
from mynah.tools import apps, windows, vault

def test_tool_registry_register():
    registry = ToolRegistry()
    registry.register("test_tool", "A dummy test tool", "safe", lambda x: f"hello {x}")
    assert "test_tool" in registry.registry
    assert registry.registry["test_tool"]["risk"] == "safe"

def test_tool_registry_execute():
    registry = ToolRegistry()
    registry.register("greet", "Greets a user", "safe", lambda name: f"Hello {name}")
    res = registry.execute("greet", {"name": "Mynah"})
    assert res == "Hello Mynah"

def test_tool_registry_missing():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.execute("unknown_tool", {})

def test_apps_launch():
    res = apps.launch("Slack")
    assert "Slack" in res

def test_apps_quit():
    res = apps.quit_app("Slack")
    assert "Slack" in res

def test_windows_snap_left():
    res = windows.snap_left()
    assert "left" in res.lower()

def test_windows_snap_right():
    res = windows.snap_right()
    assert "right" in res.lower()

def test_vault_append():
    res = vault.append("Test note")
    assert "Test note" in res

# mynah/tools/base.py
from typing import Callable, Any, Dict

class ToolRegistry:
    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, classification: str, func: Callable):
        """
        Register a tool.
        classification: 'safe' or 'irreversible'
        """
        self.registry[name] = {
            "description": description,
            "classification": classification,
            "func": func
        }

    def execute(self, name: str, args: dict) -> Any:
        if name not in self.registry:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self.registry[name]["func"](**args)

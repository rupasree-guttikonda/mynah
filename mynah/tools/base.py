# mynah/tools/base.py
from typing import Callable, Any, Dict

class ToolRegistry:
    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, risk: str, func: Callable, parameters: dict = None):
        """
        Register a tool.
        risk: MUST be either 'safe' or 'irreversible'.
        If risk is missing or invalid, raises ValueError.
        """
        if risk not in ("safe", "irreversible"):
            raise ValueError(
                f"Tool '{name}' registration failed: 'risk' must be 'safe' or 'irreversible'. Got '{risk}'."
            )
            
        self.registry[name] = {
            "description": description,
            "risk": risk,
            "func": func,
            "parameters": parameters or {"type": "object", "properties": {}}
        }

    def execute(self, name: str, args: dict) -> Any:
        if name not in self.registry:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self.registry[name]["func"](**args)

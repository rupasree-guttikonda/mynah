# mynah/safety/gate.py
"""
Safety gate mechanism for protecting irreversible tool actions.
"""

import sys
import select
import logging

from mynah.tools.base import ToolRegistry

logger = logging.getLogger("mynah.gate")

def wait_for_confirmation() -> bool:
    """Waits for keyboard or stdin confirmation with a 10-second timeout."""
    print("Confirm execution? [y/N] (10s timeout): ", end="", flush=True)
    try:
        # 10 second timeout waiting for input
        rlist, _, _ = select.select([sys.stdin], [], [], 10.0)
        if rlist:
            ans = sys.stdin.readline().strip().lower()
            return ans in ("y", "yes")
        else:
            print("\nTimeout: Execution auto-refused.")
            return False
    except Exception as e:
        logger.warning(f"Error during confirmation input: {str(e)}")
        return False

def check(registry: ToolRegistry, tool_name: str, args: dict) -> bool:
    """
    Checks the risk level of the tool.
    - 'safe': Automatically approved (returns True).
    - 'irreversible': Speaks/prints warning, requests confirmation.
    """
    if tool_name not in registry.registry:
        # Unregistered tool, fail safe
        return False
        
    tool_info = registry.registry[tool_name]
    risk = tool_info.get("risk", "irreversible")
    
    if risk == "safe":
        return True
        
    # Irreversible tool execution safety check
    print(f"\n[!!! SAFETY GATE WARNING: IRREVERSIBLE ACTION !!!]")
    print(f"Mynah is attempting to execute tool: '{tool_name}'")
    print(f"Arguments: {args}")
    
    # In a full voice implementation, this triggers TTS "Are you sure?"
    confirmed = wait_for_confirmation()
    if confirmed:
        print("[APPROVED] Executing irreversible tool.")
        return True
    else:
        print("[REFUSED] Aborting irreversible tool.")
        return False

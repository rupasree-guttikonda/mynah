#!/usr/bin/env python3
"""
Mynah Voice Assistant - Main process loop and tool routing entrypoint.
"""

import sys
import os
import argparse
import time

from mynah.log.audit import init_db, log_turn
from mynah.tools.base import ToolRegistry
import mynah.tools.apps as apps
import mynah.tools.windows as windows
import mynah.tools.vault as vault
from mynah.router.rules import RuleRouter

def setup_registry() -> ToolRegistry:
    """Creates the tool registry and registers Week 1 commands."""
    registry = ToolRegistry()
    
    # Safe tools
    registry.register("apps.launch", "Launches or focuses a macOS application by name.", "safe", apps.launch)
    registry.register("apps.quit", "Quits a macOS application by name.", "safe", apps.quit_app)
    registry.register("windows.set_volume", "Sets the macOS output volume (0-100).", "safe", windows.set_volume)
    registry.register("windows.mute", "Mutes system audio.", "safe", windows.mute)
    registry.register("windows.unmute", "Unmutes system audio.", "safe", windows.unmute)
    registry.register("windows.get_time", "Retrieves the current spoken-friendly time.", "safe", windows.get_time)
    registry.register("windows.snap_left", "Snaps window left.", "safe", windows.snap_left)
    registry.register("windows.snap_right", "Snaps window right.", "safe", windows.snap_right)
    registry.register("vault.append", "Appends a voice note entry to the daily vault logs.", "safe", vault.append)
    
    return registry

def route_and_execute(text: str, registry: ToolRegistry, router: RuleRouter) -> dict:
    """
    Simulates routing and execution of a text command.
    Logs the latency, matched tier, tool, arguments, and result.
    """
    start_time = time.time()
    
    # Run Tier 0 Rule Router
    route_result = router.route(text)
    latency_route = time.time() - start_time
    
    turn_data = {
        "transcript": text,
        "frontmost_app": "Terminal", # Mock value
        "path": os.getcwd(),
        "confidence": 1.0,
        "latency_stt": 0.0, # Mock
        "latency_route": latency_route,
        "confirmed": False,
        "repeated": False
    }
    
    if route_result:
        tool_name = route_result["tool"]
        args = route_result["args"]
        
        turn_data["tool"] = tool_name
        turn_data["args"] = args
        turn_data["matched_tier"] = 0
        
        # Execute tool
        exec_start = time.time()
        try:
            result = registry.execute(tool_name, args)
            turn_data["result"] = result
        except Exception as e:
            turn_data["result"] = f"Execution error: {str(e)}"
        turn_data["latency_exec"] = time.time() - exec_start
    else:
        turn_data["tool"] = None
        turn_data["args"] = {}
        turn_data["matched_tier"] = -1 # Unmatched / missed
        turn_data["result"] = f"Command not recognized: '{text}'"
        turn_data["latency_exec"] = 0.0
        
    # Log to SQLite turns table
    log_turn(turn_data)
    
    return turn_data

def main():
    parser = argparse.ArgumentParser(description="Mynah Voice Assistant Shell")
    parser.add_argument("--mock-text", type=str, help="Simulate a spoken command")
    parser.add_argument("--interactive", action="store_true", help="Start an interactive console session")
    args = parser.parse_args()

    # Initialize Audit Database
    init_db()
    
    # Initialize Registry and Router
    registry = setup_registry()
    router = RuleRouter()

    if args.mock_text:
        # Mock mode
        print(f"Routing mock command: '{args.mock_text}'")
        turn = route_and_execute(args.mock_text, registry, router)
        print(f"Result: {turn['result']}")
        print(f"Logged to SQLite in audit.db (Tier {turn['matched_tier']})")
    elif args.interactive:
        # Interactive shell mode
        print("Mynah Interactive Shell. Type a command or 'exit' to quit.")
        while True:
            try:
                cmd = input("Mynah > ").strip()
                if cmd.lower() in ["exit", "quit"]:
                    break
                if not cmd:
                    continue
                turn = route_and_execute(cmd, registry, router)
                print(f"Response: {turn['result']}")
            except KeyboardInterrupt:
                break
        print("\nExited Mynah Interactive Shell.")
    else:
        # Default behavior: print help
        parser.print_help()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mynah Voice Assistant - Main process loop and tool routing entrypoint.
"""

import sys
import os
import argparse
import time
import datetime

from mynah.log.audit import init_db, log_turn
from mynah.tools.base import ToolRegistry
import mynah.tools.apps as apps
import mynah.tools.windows as windows
import mynah.tools.vault as vault
import mynah.tools.keychain as keychain

from mynah.router.rules import RuleRouter
from mynah.memory.context import get_active_context
from mynah.router.brain import route_local_tool, route_cloud_fallback, assess_confidence
import mynah.safety.gate as gate

def setup_registry() -> ToolRegistry:
    """Creates the tool registry and registers tools with strict risk labels and parameters."""
    registry = ToolRegistry()
    
    # apps.launch
    registry.register(
        "apps.launch",
        "Launches or focuses a macOS application by name.",
        "safe",
        apps.launch,
        {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The exact name of the macOS application to launch (e.g. Safari, Terminal, Calculator)."
                }
            },
            "required": ["name"]
        }
    )
    
    # apps.quit
    registry.register(
        "apps.quit",
        "Quits a macOS application by name.",
        "safe",
        apps.quit_app,
        {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the application to quit."
                }
            },
            "required": ["name"]
        }
    )
    
    # windows.set_volume
    registry.register(
        "windows.set_volume",
        "Sets the macOS output volume (0-100).",
        "safe",
        windows.set_volume,
        {
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer",
                    "description": "The target volume level from 0 to 100."
                }
            },
            "required": ["level"]
        }
    )
    
    # volume controls without params
    registry.register("windows.mute", "Mutes system audio.", "safe", windows.mute)
    registry.register("windows.unmute", "Unmutes system audio.", "safe", windows.unmute)
    registry.register("windows.get_time", "Retrieves the current spoken-friendly time.", "safe", windows.get_time)
    registry.register("windows.snap_left", "Snaps window left.", "safe", windows.snap_left)
    registry.register("windows.snap_right", "Snaps window right.", "safe", windows.snap_right)
    
    # vault.append
    registry.register(
        "vault.append",
        "Appends a voice note entry to the daily vault logs.",
        "safe",
        vault.append,
        {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text content of the note to append to the daily logs."
                }
            },
            "required": ["text"]
        }
    )
    
    # vault.search
    registry.register(
        "vault.search",
        "Searches all vault notes for a query, ranked by recency.",
        "safe",
        vault.search,
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look for in the vault."
                }
            },
            "required": ["query"]
        }
    )
    
    # Irreversible tool for safety testing (e.g. system commands)
    def mock_delete_file(path: str) -> str:
        return f"Mock deleted file at path: {path}"
        
    registry.register(
        "systems.delete_file",
        "Deletes a file permanently. WARNING: This action is irreversible.",
        "irreversible",
        mock_delete_file,
        {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to delete."
                }
            },
            "required": ["path"]
        }
    )
    # keychain.set_secret
    registry.register(
        "keychain.set_secret",
        "Saves a password or token securely in the macOS Keychain. WARNING: This action is irreversible.",
        "irreversible",
        keychain.set_secret,
        {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "The service name for the secret."
                },
                "account": {
                    "type": "string",
                    "description": "The account name for the secret."
                },
                "secret": {
                    "type": "string",
                    "description": "The secret password or token value."
                }
            },
            "required": ["service", "account", "secret"]
        }
    )
    
    # keychain.get_secret
    registry.register(
        "keychain.get_secret",
        "Retrieves a secret password or token from the macOS Keychain.",
        "safe",
        keychain.get_secret,
        {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "The service name of the secret."
                },
                "account": {
                    "type": "string",
                    "description": "The account name of the secret."
                }
            },
            "required": ["service", "account"]
        }
    )
    
    return registry

def is_question_pattern(text: str) -> bool:
    """
    Detects if a prompt is a general knowledge question that should bypass Tier 1.
    If the prompt contains keywords related to registered tools, it is treated as a command
    and NOT bypassed, so the local model can handle it.
    """
    words = ["what", "why", "how", "explain", "who", "when", "can you explain"]
    cleaned = text.lower().strip()
    
    # If it doesn't start with any question word, it's not a question bypass
    if not any(cleaned.startswith(w) for w in words):
        return False
        
    # If it contains tool command keywords, let it go to Tier 0 / Tier 1 instead of bypassing
    tool_keywords = [
        "time", "volume", "mute", "unmute", "snap", "window", "open", 
        "launch", "quit", "close", "note", "remember", "search", "find", 
        "delete", "file", "calendar", "keychain", "secret", "password",
        "wrote", "write", "key"
    ]
    if any(keyword in cleaned for keyword in tool_keywords):
        return False
        
    return True

def route_and_execute(text: str, registry: ToolRegistry, router: RuleRouter) -> dict:
    """
    Executes the unified Mynah routing pipeline:
    Question Check -> Tier 0 (Rules) -> Tier 1 (Local LLM) -> Tier 2 (Cloud Fallback) -> Gate -> Executor.
    """
    start_time = time.time()
    
    turn_data = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transcript": text,
        "frontmost_app": "Terminal", # Default app
        "path": os.getcwd(),
        "confidence": 1.0,
        "matched_tier": -1,
        "tool": None,
        "args": "{}",
        "result": "",
        "cost_usd": 0.0,
        "latency_stt": 0.0,
        "latency_route": 0.0,
        "latency_exec": 0.0,
        "confirmed": False,
        "repeated": False
    }

    # 1. Question Pattern Check (Fix 3)
    if is_question_pattern(text):
        print("[TIER BYPASS] Question detected. Routing directly to Tier 2 Cloud.")
        context = get_active_context()
        route_result = route_cloud_fallback(text, context, registry)
        turn_data["matched_tier"] = 2
        turn_data["latency_route"] = time.time() - start_time
        process_llm_result(route_result, turn_data, registry)
        
    else:
        # 2. Tier 0 Rule matching
        route_result = router.route(text)
        if route_result:
            turn_data["matched_tier"] = 0
            turn_data["tool"] = route_result["tool"]
            import json
            turn_data["args"] = json.dumps(route_result["args"])
            turn_data["latency_route"] = time.time() - start_time
            
            # Execute safety gate and run tool
            exec_start = time.time()
            if gate.check(registry, route_result["tool"], route_result["args"]):
                turn_data["confirmed"] = True
                try:
                    res = registry.execute(route_result["tool"], route_result["args"])
                    turn_data["result"] = str(res)
                except Exception as e:
                    turn_data["result"] = f"Execution error: {str(e)}"
            else:
                turn_data["result"] = "Execution refused by safety gate."
            turn_data["latency_exec"] = time.time() - exec_start
            
        else:
            # Tier 0 Miss -> Gather context for models
            context = get_active_context()
            
            # 3. Tier 1 Local LLM tool call
            local_start = time.time()
            local_result = route_local_tool(text, context, registry)
            
            # Check local confidence (Fix 8)
            if assess_confidence(local_result, registry):
                turn_data["matched_tier"] = 1
                turn_data["latency_route"] = time.time() - start_time
                process_llm_result(local_result, turn_data, registry)
            else:
                print("[TIER ESCALATION] Local model low confidence or missed. Escalating to Tier 2.")
                # 4. Tier 2 Cloud escalation
                cloud_result = route_cloud_fallback(text, context, registry)
                turn_data["matched_tier"] = 2
                turn_data["latency_route"] = time.time() - start_time
                process_llm_result(cloud_result, turn_data, registry)

    # 5. Log every single turn to SQLite (Fix 12)
    log_turn(turn_data)
    return turn_data

def process_llm_result(result: dict, turn_data: dict, registry: ToolRegistry):
    """Executes the tool or returns direct spoken text based on LLM outputs."""
    import json
    
    # Spend costing record
    turn_data["cost_usd"] = result.get("cost_usd", 0.0)
    
    r_type = result.get("type")
    
    if r_type == "tool":
        tool_name = result["tool"]
        args = result["args"]
        turn_data["tool"] = tool_name
        turn_data["args"] = json.dumps(args)
        
        exec_start = time.time()
        # Verify Safety Gate (Fix 1)
        if gate.check(registry, tool_name, args):
            turn_data["confirmed"] = True
            try:
                res = registry.execute(tool_name, args)
                turn_data["result"] = str(res)
            except Exception as e:
                turn_data["result"] = f"Execution error: {str(e)}"
        else:
            turn_data["result"] = "Execution refused by safety gate."
        turn_data["latency_exec"] = time.time() - exec_start
        
    elif r_type == "text":
        turn_data["result"] = result["content"]
        
    elif r_type == "refusal":
        # Budget limit refusal logged cleanly (Fix 11)
        turn_data["result"] = f"Aborted: {result['content']}"
        print(f"Mynah: {result['content']}")
        
    else:
        # Error
        turn_data["result"] = result.get("content", "Unknown routing error.")

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
        print(f"Routing mock command: '{args.mock_text}'")
        turn = route_and_execute(args.mock_text, registry, router)
        print(f"Result: {turn['result']}")
    elif args.interactive:
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
        parser.print_help()

if __name__ == "__main__":
    main()

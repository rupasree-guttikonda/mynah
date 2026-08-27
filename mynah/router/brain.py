# mynah/router/brain.py
"""
Tier 1 (Local LLM) and Tier 2 (Cloud LLM) routing engine for Mynah.
Uses unified OpenAI client library wrappers.
"""

import os
import sqlite3
import datetime
import logging
import openai
from typing import Dict, Any, List

from mynah.config import get_default_local_model, OPENAI_MODEL, DAILY_BUDGET_LIMIT
from mynah.tools.base import ToolRegistry

logger = logging.getLogger("mynah.brain")

# Client initializers
def get_local_client() -> openai.OpenAI:
    return openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def get_cloud_client() -> openai.OpenAI:
    return openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key"))

def get_daily_spend() -> float:
    """Queries the SQLite audit log to find the total USD spend for today."""
    db_path = "audit.db"
    if not os.path.exists(db_path):
        return 0.0
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # Query sum where ts starts with today's date YYYY-MM-DD
        cursor.execute("SELECT SUM(cost_usd) FROM turns WHERE ts LIKE ?", (f"{today}%",))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] is not None else 0.0
    except Exception as e:
        logger.warning(f"Failed to calculate daily spend: {str(e)}")
        return 0.0

def build_openai_tools(registry: ToolRegistry) -> List[Dict[str, Any]]:
    """Formats Mynah's registered tools into OpenAI Tool Call specifications."""
    tools = []
    for name, info in registry.registry.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
        })
    return tools

def assess_confidence(route_result: dict, registry: ToolRegistry) -> bool:
    """
    Validates a tool routing result against registered schemas to assess confidence.
    Escalates to cloud (returns False) on any schema or type failures.
    """
    if not route_result or route_result.get("type") != "tool":
        return False
        
    tool_name = route_result.get("tool")
    args = route_result.get("args", {})
    
    # 1. Tool name must be in the registry
    if tool_name not in registry.registry:
        return False
        
    tool_info = registry.registry[tool_name]
    parameters = tool_info.get("parameters", {})
    properties = parameters.get("properties", {})
    required = parameters.get("required", [])
    
    # 2. Check all required arguments are present and not empty
    for req in required:
        if req not in args:
            return False
        val = args[req]
        if val is None or (isinstance(val, str) and val.strip() == ""):
            return False
            
    # 3. Simple type checking
    for key, value in args.items():
        if key not in properties:
            # Extra arguments not in schema
            return False
        expected_type = properties[key].get("type")
        if expected_type == "string" and not isinstance(value, str):
            return False
        elif expected_type == "integer" and not isinstance(value, int) and not (isinstance(value, float) and value.is_integer()):
            return False
        elif expected_type == "boolean" and not isinstance(value, bool):
            return False
            
    return True

def route_local_tool(text: str, context: str, registry: ToolRegistry) -> dict:
    """
    Tier 1 Routing: Queries Ollama for local tool calling with structured outputs.
    """
    model_name = get_default_local_model()
    openai_tools = build_openai_tools(registry)
    
    try:
        client = get_local_client()
        # Call local model
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": f"You are Mynah, a local voice assistant. Use the tools provided to fulfill the request. Context:\n{context}"},
                {"role": "user", "content": text}
            ],
            tools=openai_tools,
            tool_choice="auto",
            temperature=0.0 # Greedy decoding for routing stability
        )
        
        message = response.choices[0].message
        if message.tool_calls:
            # Extract first tool call
            tool_call = message.tool_calls[0].function
            import json
            try:
                args = json.loads(tool_call.arguments)
            except Exception:
                args = {}
            return {
                "type": "tool",
                "tool": tool_call.name,
                "args": args
            }
        else:
            return {
                "type": "text",
                "content": message.content or ""
            }
            
    except Exception as e:
        logger.warning(f"Ollama local routing query failed: {str(e)}")
        return {
            "type": "error",
            "content": f"Local routing error: {str(e)}"
        }

def route_cloud_fallback(text: str, context: str, registry: ToolRegistry) -> dict:
    """
    Tier 2 Routing: Escalates query to OpenAI gpt-4o-mini with cost monitoring and budget enforcement.
    """
    # 1. Budget ceiling enforcement (Fix 11)
    current_spend = get_daily_spend()
    if current_spend >= DAILY_BUDGET_LIMIT:
        return {
            "type": "refusal",
            "content": "Daily spend limit reached."
        }
        
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "type": "error",
            "content": "OpenAI API key missing in environment."
        }
        
    openai_tools = build_openai_tools(registry)
    
    try:
        client = get_cloud_client()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"You are Mynah, a voice assistant. Respond concisely. Use tools if needed. Context:\n{context}"},
                {"role": "user", "content": text}
            ],
            tools=openai_tools,
            tool_choice="auto"
        )
        
        # Calculate actual cost (Fix 10)
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        cost_usd = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)
        
        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0].function
            import json
            try:
                args = json.loads(tool_call.arguments)
            except Exception:
                args = {}
            return {
                "type": "tool",
                "tool": tool_call.name,
                "args": args,
                "cost_usd": cost_usd
            }
        else:
            return {
                "type": "text",
                "content": message.content or "",
                "cost_usd": cost_usd
            }
            
    except Exception as e:
        logger.warning(f"Cloud OpenAI fallback query failed: {str(e)}")
        return {
            "type": "error",
            "content": f"Cloud routing error: {str(e)}"
        }

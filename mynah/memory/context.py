# mynah/memory/context.py
"""
Context injection engine for Mynah. Aggregates local profile markdown files,
caching active macOS window information, and querying recent conversation history.
"""

import os
import time
import sqlite3
import logging
import subprocess
import tiktoken

from mynah.config import VAULT_DIR

# Set up logging for warnings
logger = logging.getLogger("mynah.context")

# Global window state cache
_window_cache = {"data": None, "timestamp": 0.0}

def count_tokens(text: str) -> int:
    """Returns the token count of the text using tiktoken's gpt-4o-mini encoding."""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        return len(encoding.encode(text))
    except Exception:
        # Fallback fallback approximation: ~4 characters per token
        return len(text) // 4

def get_active_window_info() -> dict:
    """
    Queries macOS via AppleScript to find the frontmost app name and active window title.
    Caches results with a 2-second TTL to keep routing sub-100ms.
    """
    now = time.time()
    if now - _window_cache["timestamp"] < 2.0 and _window_cache["data"] is not None:
        return _window_cache["data"]

    # AppleScript to fetch frontmost app and window title
    applescript = """
    global frontApp, windowTitle
    set windowTitle to ""
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
        try
            tell process frontApp
                set windowTitle to name of first window
            end tell
        end try
    end tell
    return frontApp & "|||" & windowTitle
    """
    try:
        res = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            timeout=1.0
        )
        if res.returncode == 0:
            parts = res.stdout.strip().split("|||")
            app_name = parts[0] if len(parts) > 0 else "Unknown"
            window_title = parts[1] if len(parts) > 1 and parts[1] else "No Active Window"
            data = {"app": app_name, "window": window_title}
        else:
            data = {"app": "Terminal", "window": "Active Session"}
    except Exception:
        data = {"app": "Terminal", "window": "Active Session"}

    _window_cache["data"] = data
    _window_cache["timestamp"] = now
    return data

def get_recent_history() -> str:
    """Retrieves the last two conversation turns from the SQLite database."""
    history = []
    # Path to SQLite DB
    db_path = "audit.db"
    if not os.path.exists(db_path):
        return "No recent conversation history."
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Query last 2 turns in chronological order
        cursor.execute("""
            SELECT transcript, tool, result FROM turns 
            ORDER BY rowid DESC LIMIT 2
        """)
        rows = cursor.fetchall()
        conn.close()
        
        # Format in reverse (oldest of the two first)
        for row in reversed(rows):
            prompt, tool, result = row
            tool_str = f"Executed: {tool}" if tool else "No tool executed"
            history.append(f"User: {prompt}\nSystem ({tool_str}): {result}")
            
    except Exception as e:
        logger.warning(f"Failed to query conversation history: {str(e)}")
        
    if not history:
        return "No recent conversation history."
    return "\n---\n".join(history)

def get_profile_context() -> str:
    """
    Reads identity, work, and preferences markdown files from vault/me/.
    Hard-caps context payload at 500 tokens.
    """
    profile_text = ""
    me_dir = os.path.join(VAULT_DIR, "me")
    if not os.path.exists(me_dir):
        return "No identity profile context available."

    files_to_read = ["identity.md", "work.md", "preferences.md"]
    for file_name in files_to_read:
        file_path = os.path.join(me_dir, file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                profile_text += f"\n### {file_name}\n{content}\n"
            except Exception as e:
                logger.warning(f"Could not read profile file {file_name}: {str(e)}")

    # Check token count and enforce 500-token limit (Fix 6)
    token_count = count_tokens(profile_text)
    if token_count > 500:
        logger.warning(f"Vault profile context exceeds 500 tokens (got {token_count}). Truncating context.")
        # Truncate text context safely
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoding.encode(profile_text)[:500]
        profile_text = encoding.decode(tokens) + "\n[... Context Truncated ...]"

    return profile_text.strip()

def get_active_context() -> str:
    """Aggregates active window, profile files, and recent history into a prompt context string."""
    window = get_active_window_info()
    window_str = f"Active App: {window['app']}\nActive Window: {window['window']}"
    
    profiles = get_profile_context()
    history = get_recent_history()
    
    context_template = f"""[MYNAH RUNTIME SYSTEM CONTEXT]

[OS WINDOW STATE]
{window_str}

[USER PROFILE & PREFERENCES]
{profiles}

[RECENT CONVERSATION HISTORY]
{history}
"""
    return context_template

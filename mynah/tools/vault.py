# mynah/tools/vault.py
"""
Vault operations tools (note capturing, search, recall).
"""

import os
import datetime

VAULT_DIR = "vault"
DAILY_DIR = os.path.join(VAULT_DIR, "daily")

def append(text: str) -> str:
    """Appends a timestamped voice note to the daily vault log file."""
    # Ensure daily directory exists
    os.makedirs(DAILY_DIR, exist_ok=True)
    
    # Get today's date and time
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    file_path = os.path.join(DAILY_DIR, f"{date_str}.md")
    
    # Format entry
    entry = f"- **{time_str}**: {text}\n"
    
    try:
        # Check if file exists, if not write header
        is_new = not os.path.exists(file_path)
        with open(file_path, "a") as f:
            if is_new:
                f.write(f"# Daily Log — {date_str}\n\n")
            f.write(entry)
        return f"Successfully appended note to daily log: {text}"
    except Exception as e:
        return f"Failed to save note to vault: {str(e)}"

# mynah/memory/compaction.py
"""
Week 6 Tasks: Daily Compaction Service.
Reads daily notes, extracts personal facts using local LLM,
and promotes updates to identity, work history, and preference profiles.
"""

import os
import json
import datetime
import logging
from mynah.config import get_default_local_model
from mynah.router.brain import get_local_client

logger = logging.getLogger("mynah.compaction")

VAULT_DAILY_DIR = os.getenv("MYNAH_VAULT_DAILY_DIR", os.path.join("vault", "daily"))
VAULT_ME_DIR = os.getenv("MYNAH_VAULT_ME_DIR", os.path.join("vault", "me"))

def compact_daily_log(date_str: str) -> str:
    """
    Summarizes updates from vault/daily/YYYY-MM-DD.md and appends/promotes
    relevant facts to identity.md, work.md, and preferences.md.
    """
    daily_file = os.path.join(VAULT_DAILY_DIR, f"{date_str}.md")
    if not os.path.exists(daily_file):
        logger.info(f"Daily log for {date_str} not found at {daily_file}. Skipping compaction.")
        return f"No daily log found for {date_str}."
        
    with open(daily_file, "r") as f:
        daily_content = f.read()
        
    if not daily_content.strip():
        return "Daily log is empty. Nothing to compact."
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"""You are an expert personal data analyst. Analyze this user's daily log notes for the day: {date_str}.
Identify if there are any new updates or modifications to the user's:
1. "identity": changes to names, locations, target job titles/roles, contact info.
2. "work": accomplishments, projects completed, resume updates, new work experiences.
3. "preferences": salary desires, sponsorship requirements, remote policy preferences, new answers to standard job application questions.

Return a JSON object containing lists of strings for the updates found, using these exact keys:
- "identity_updates": list of strings to add to identity.md (e.g. "- Added Target Role: AI Platform Engineer")
- "work_updates": list of strings to add to work.md (e.g. "- Implemented SQLite audit logs and pytest suites")
- "preference_updates": list of strings to add to preferences.md (e.g. "- Desired Salary updated to $150,000")

Daily Log Content:
{daily_content}
"""

    try:
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You must output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=30.0
        )
        content = response.choices[0].message.content
        updates = json.loads(content)
        
        # Apply updates to profile markdown files
        promoted_count = 0
        
        identity_file = os.path.join(VAULT_ME_DIR, "identity.md")
        if updates.get("identity_updates"):
            append_updates_to_file(identity_file, updates["identity_updates"], date_str)
            promoted_count += len(updates["identity_updates"])
            
        work_file = os.path.join(VAULT_ME_DIR, "work.md")
        if updates.get("work_updates"):
            append_updates_to_file(work_file, updates["work_updates"], date_str)
            promoted_count += len(updates["work_updates"])
            
        pref_file = os.path.join(VAULT_ME_DIR, "preferences.md")
        if updates.get("preference_updates"):
            append_updates_to_file(pref_file, updates["preference_updates"], date_str)
            promoted_count += len(updates["preference_updates"])
            
        return f"Successfully compacted daily log. Promoted {promoted_count} items to profile vault."
    except Exception as e:
        logger.warning(f"Failed to compact daily log: {str(e)}")
        return f"Compaction failed: {str(e)}"

def append_updates_to_file(file_path: str, updates: list, date_str: str):
    """Safely appends list items under a header block without destroying frontmatter."""
    if not updates:
        return
        
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Read existing content if it exists
    content = ""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
            
    # Add new section block
    update_block = f"\n\n## Compacted Updates from {date_str}\n"
    for item in updates:
        if not item.startswith("-"):
            update_block += f"- {item}\n"
        else:
            update_block += f"{item}\n"
            
    with open(file_path, "w") as f:
        f.write(content.strip() + update_block)

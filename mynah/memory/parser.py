# mynah/memory/parser.py
"""
Week 6 Tasks: Meeting Parser.
Cleans raw transcript streams, extracts participants, decisions, and action items,
and saves them under vault/meetings/YYYY-MM-DD_[title].md.
"""

import os
import json
import datetime
import logging
from mynah.config import get_default_local_model
from mynah.router.brain import get_local_client

logger = logging.getLogger("mynah.parser")
VAULT_MEETINGS_DIR = os.getenv("MYNAH_VAULT_MEETINGS_DIR", os.path.join("vault", "meetings"))

def parse_meeting_transcript(raw_text: str) -> dict:
    """
    Cleans up raw transcripts and extracts meeting structure (title, participants, decisions, action_items)
    using the default local Ollama model in JSON mode.
    """
    if not raw_text.strip():
        return {
            "title": "Untitled Meeting",
            "participants": [],
            "decisions": [],
            "action_items": []
        }
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"""You are a helpful office assistant. Analyze the following raw transcript of a meeting.
Extract the key meeting structures and return them as a JSON object with these keys:
- "title": A concise, descriptive title for the meeting.
- "participants": A list of strings representing the names of participants or speakers.
- "decisions": A list of strings representing key decisions made.
- "action_items": A list of dicts, where each dict has keys "owner" (name of person) and "task" (what they need to do).

Raw Transcript:
{raw_text}
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
        data = json.loads(content)
        return {
            "title": data.get("title", "Untitled Meeting"),
            "participants": data.get("participants", []),
            "decisions": data.get("decisions", []),
            "action_items": data.get("action_items", [])
        }
    except Exception as e:
        logger.warning(f"Failed to parse transcript via local LLM: {str(e)}")
        # Return structured format with fallback tasks
        return {
            "title": "Meeting log",
            "participants": [],
            "decisions": [],
            "action_items": [{"owner": "Unknown", "task": "Verify manual extraction from raw transcript"}]
        }

def save_meeting_log(parsed_data: dict) -> str:
    """
    Saves the extracted meeting log as a markdown file under vault/meetings/YYYY-MM-DD_[title].md.
    """
    os.makedirs(VAULT_MEETINGS_DIR, exist_ok=True)
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    title_slug = parsed_data["title"].lower().replace(" ", "_")
    # Clean up non-alphanumeric chars for filename
    title_slug = "".join(c for c in title_slug if c.isalnum() or c == "_")[:50]
    
    filename = f"{date_str}_{title_slug}.md"
    file_path = os.path.join(VAULT_MEETINGS_DIR, filename)
    
    participants_str = "\n".join(f"- {p}" for p in parsed_data["participants"]) if parsed_data["participants"] else "None detected."
    decisions_str = "\n".join(f"- {d}" for d in parsed_data["decisions"]) if parsed_data["decisions"] else "None recorded."
    
    md_content = f"""# Meeting: {parsed_data['title']}
Date: {date_str}

## Participants
{participants_str}

## Decisions Made
{decisions_str}

## Action Items
"""
    if parsed_data['action_items']:
        for item in parsed_data['action_items']:
            owner = item.get("owner", "Unassigned")
            task = item.get("task", "")
            md_content += f"- **[{owner}]**: {task}\n"
    else:
        md_content += "None assigned.\n"
        
    with open(file_path, "w") as f:
        f.write(md_content)
        
    return file_path

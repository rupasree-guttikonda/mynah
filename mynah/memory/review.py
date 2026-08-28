# mynah/memory/review.py
"""
Memory Review tools: interactive quiz generation and monthly summary extraction.
"""

import os
import glob
import random
import datetime
import logging
from mynah.config import get_default_local_model
from mynah.router.brain import get_local_client

logger = logging.getLogger("mynah.review")

VAULT_DAILY_DIR = os.getenv("MYNAH_VAULT_DAILY_DIR", os.path.join("vault", "daily"))
VAULT_ME_DIR = os.getenv("MYNAH_VAULT_ME_DIR", os.path.join("vault", "me"))

def quiz_me() -> str:
    """Selects a random note from vault/daily/ or vault/me/, and generates a quiz question."""
    files = []
    
    # Gather files from daily logs
    if os.path.exists(VAULT_DAILY_DIR):
        files.extend(glob.glob(os.path.join(VAULT_DAILY_DIR, "*.md")))
        
    # Gather files from me profiles
    if os.path.exists(VAULT_ME_DIR):
        files.extend(glob.glob(os.path.join(VAULT_ME_DIR, "*.md")))
        
    if not files:
        return "I couldn't find any notes in your vault to quiz you on. Try adding some daily notes first."
        
    # Select a random file
    selected_file = random.choice(files)
    filename = os.path.basename(selected_file)
    
    try:
        with open(selected_file, "r") as f:
            content = f.read().strip()
            
        if not content:
            return f"The note {filename} is empty. Let me try again."
            
        local_model = get_default_local_model()
        client = get_local_client()
        
        prompt = f"""Based on the following personal note '{filename}', generate one interactive quiz question to test my memory about what happened or what was decided.
Provide 3 multiple-choice options (A, B, C). Do not reveal the correct answer in the question text.

Note Content:
\"\"\"
{content}
\"\"\"
"""
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You are a helpful memory coach. Ask a single multiple-choice question based on the note provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            timeout=25.0
        )
        return f"Memory Quiz from '{filename}':\n\n{response.choices[0].message.content.strip()}"
    except Exception as e:
        logger.warning(f"Quiz generation failed: {e}")
        return f"Failed to generate quiz: {str(e)}"

def summarize_month() -> str:
    """Aggregates all daily logs from the last 30 days and summarizes learnings/accomplishments."""
    if not os.path.exists(VAULT_DAILY_DIR):
        return "No daily logs found. I need some daily logs to summarize your month."
        
    today = datetime.date.today()
    log_contents = []
    
    # Read files from last 30 days
    for i in range(30):
        check_date = today - datetime.timedelta(days=i)
        date_str = check_date.strftime("%Y-%m-%d")
        daily_file = os.path.join(VAULT_DAILY_DIR, f"{date_str}.md")
        
        if os.path.exists(daily_file):
            try:
                with open(daily_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        log_contents.append(f"--- Date: {date_str} ---\n{content}")
            except Exception as e:
                logger.warning(f"Error reading daily log {daily_file}: {e}")
                
    if not log_contents:
        return "You have no daily notes from the past 30 days. Add some daily logs to get a monthly summary."
        
    # Concatenate log files, capping to avoid context limit
    full_text = "\n\n".join(log_contents)
    if len(full_text) > 15000:
        full_text = full_text[:15000] + "\n...[Content Truncated]..."
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"""Here are my daily logs from the past month:
{full_text}

Analyze these logs and compile a comprehensive summary of:
1. My major achievements and completed projects.
2. My main learnings, updates to preferences, or feedback notes.
Keep the output structured with clear headers.
"""
    try:
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You are a professional assistant specializing in personal logs summarization. Be structured, positive, and clear."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            timeout=30.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Monthly summary generation failed: {e}")
        return f"Failed to generate monthly summary: {str(e)}"

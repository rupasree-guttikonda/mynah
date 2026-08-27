# mynah/memory/formatter.py
"""
Utility functions to format text outputs into natural, spoken-friendly responses
with clear source attribution.
"""

import datetime
import os

def format_spoken_response(text: str, source_metadata: dict = None) -> str:
    """
    Formats raw information retrieved from the vault into a natural, spoken-friendly response
    with explicit verbal source attribution.
    
    source_metadata keys:
        - "type": "identity" | "work_history" | "application_preferences" | "daily_log" | "quarantine"
        - "file_name": str (e.g., "identity.md" or "2026-08-26.md")
        - "date": str (e.g., "2026-08-26")
        - "source": str (e.g., "Safari Webpage")
    """
    if not source_metadata:
        return text
        
    attribution = ""
    m_type = source_metadata.get("type")
    file_name = source_metadata.get("file_name", "")
    date_str = source_metadata.get("date")
    source = source_metadata.get("source")
    
    # 1. Parse date for a friendly spoken format (e.g., "August 26th")
    friendly_date = ""
    if date_str:
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # Day suffix: 1st, 2nd, 3rd, 4th...
            day = dt.day
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]
            friendly_date = dt.strftime(f"%B {day}{suffix}")
        except ValueError:
            friendly_date = date_str
            
    # 2. Construct attribution based on the source type
    if m_type == "identity":
        attribution = "According to your identity profile"
    elif m_type == "work_history":
        attribution = "Based on your work history records"
    elif m_type == "application_preferences":
        attribution = "According to your job application preferences"
    elif m_type == "daily_log" and friendly_date:
        attribution = f"From your daily note on {friendly_date}"
    elif m_type == "daily_log":
        attribution = "From your daily notes"
    elif m_type == "quarantine" and source:
        attribution = f"From the quarantined content captured from {source}"
    elif file_name:
        attribution = f"From your note in {file_name}"
    else:
        attribution = "According to your notes"
        
    # Combine attribution and content naturally
    clean_text = text.strip()
    if clean_text:
        return f"{attribution}, {clean_text}"
    return attribution + "."

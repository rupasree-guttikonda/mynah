# mynah/tools/clipboard.py
"""
macOS Native Clipboard Actions.
"""

import subprocess
import logging
from mynah.config import get_default_local_model
from mynah.router.brain import get_local_client

logger = logging.getLogger("mynah.clipboard")

def read_clipboard() -> str:
    """Reads text from macOS pasteboard natively (AppKit) or falls back to pbpaste."""
    try:
        from AppKit import NSPasteboard, NSStringPboardType
        pb = NSPasteboard.generalPasteboard()
        text = pb.stringForType_(NSStringPboardType)
        if text:
            return text
    except ImportError:
        pass
    
    # Fallback to pbpaste
    try:
        res = subprocess.run(["/usr/bin/pbpaste"], capture_output=True, text=True, timeout=2.0)
        if res.returncode == 0:
            return res.stdout
    except Exception as e:
        logger.warning(f"Failed to read clipboard: {e}")
    return ""

def explain_code() -> str:
    """Reads code from the clipboard and generates an explanation."""
    code = read_clipboard().strip()
    if not code:
        return "Clipboard is empty. Please copy some code to your clipboard first."
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"Explain this code concisely, focusing on its main purpose and key logic:\n\n```python\n{code}\n```"
    
    try:
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You are a helpful software engineer assistant. Keep your answer brief and clear."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            timeout=25.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Failed to explain code: {e}")
        return f"Could not explain code: {str(e)}"

def summarize_text() -> str:
    """Reads text from the clipboard and generates a summary."""
    text = read_clipboard().strip()
    if not text:
        return "Clipboard is empty. Please copy some text to your clipboard first."
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"Provide a brief, one-sentence summary of this text:\n\n{text}"
    
    try:
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You are a concise editor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            timeout=25.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Failed to summarize text: {e}")
        return f"Could not summarize text: {str(e)}"

def translate_selection(target_language: str) -> str:
    """Reads text from the clipboard and translates it to the target language."""
    text = read_clipboard().strip()
    if not text:
        return "Clipboard is empty. Please copy some text to your clipboard first."
        
    local_model = get_default_local_model()
    client = get_local_client()
    
    prompt = f"Translate this text directly to {target_language}. Output ONLY the direct translation:\n\n{text}"
    
    try:
        response = client.chat.completions.create(
            model=local_model,
            messages=[
                {"role": "system", "content": "You are a direct translator. Output the translated text only without introductions or explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            timeout=25.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Failed to translate selection: {e}")
        return f"Could not translate: {str(e)}"

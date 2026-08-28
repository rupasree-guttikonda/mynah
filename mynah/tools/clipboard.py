# mynah/tools/clipboard.py
"""
Clipboard inspection and actions.
"""
# mynah/tools/clipboard.py
"""
Clipboard inspection and actions.
Reads text currently on the macOS clipboard using PyObjC's NSPasteboard,
so voice commands like "explain this" or "summarize this" can act on
whatever the user just copied or selected.
"""

try:
    from AppKit import NSPasteboard, NSPasteboardTypeString
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False


def get_clipboard_text() -> str:
    """
    Returns the current text content of the macOS clipboard, or an empty
    string if the clipboard is empty, contains non-text data, or PyObjC's
    AppKit bindings aren't available.
    """
    if not HAS_APPKIT:
        return ""

    pasteboard = NSPasteboard.generalPasteboard()
    text = pasteboard.stringForType_(NSPasteboardTypeString)
    return text if text else ""


def set_clipboard_text(text: str) -> bool:
    """
    Writes text to the macOS clipboard, replacing its current contents.
    Returns True on success, False if AppKit isn't available or the write failed.
    """
    if not HAS_APPKIT or text is None:
        return False

    pasteboard = NSPasteboard.generalPasteboard()
    pasteboard.clearContents()
    success = pasteboard.setString_forType_(text, NSPasteboardTypeString)
    return bool(success)
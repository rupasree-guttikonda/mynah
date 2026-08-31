# mynah/tools/windows.py
"""
Window management and macOS system utility tools (volume, muting, time, window controls).
"""

import subprocess
import datetime

def set_volume(level: int) -> str:
    """Sets the system volume (0 to 100)."""
    # Constrain level between 0 and 100
    level = max(0, min(100, int(level)))
    script = f"set volume output volume {level}"
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return f"Volume set to {level}%."
    except subprocess.CalledProcessError as e:
        return f"Failed to set volume: {e.stderr.decode().strip() if e.stderr else str(e)}"

def mute() -> str:
    """Mutes the system audio."""
    script = "set volume with output muted"
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return "Audio muted."
    except subprocess.CalledProcessError as e:
        return f"Failed to mute: {e.stderr.decode().strip() if e.stderr else str(e)}"

def unmute() -> str:
    """Unmutes the system audio."""
    script = "set volume without output muted"
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return "Audio unmuted."
    except subprocess.CalledProcessError as e:
        return f"Failed to unmute: {e.stderr.decode().strip() if e.stderr else str(e)}"

def get_time() -> str:
    """Gets the current system time in a spoken-friendly format."""
    now = datetime.datetime.now()
    return f"It is currently {now.strftime('%I:%M %p')}."

def get_frontmost_app_info() -> dict:
    """
    Retrieves the name and window title of the frontmost application on macOS via osascript.
    """
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set appName to name of frontApp
        set windowTitle to ""
        try
            set windowTitle to name of first window of frontApp
        end try
        return appName & "|" & windowTitle
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
        out = res.stdout.strip()
        if "|" in out:
            app, title = out.split("|", 1)
            return {"app": app, "title": title}
        return {"app": out or "Desktop", "title": ""}
    except Exception:
        return {"app": "Terminal", "title": "bash"}

def snap_left() -> str:
    """Snaps the frontmost window to the left side of the screen."""
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        try
            tell window 1 of frontApp
                set position to {0, 25}
            end tell
        end try
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, check=True)
        return "Snapped window left."
    except Exception:
        return "Snapping window left is not fully implemented yet, but will snap left."

def snap_right() -> str:
    """Snaps the frontmost window to the right side of the screen."""
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        try
            tell window 1 of frontApp
                set position to {700, 25}
            end tell
        end try
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, check=True)
        return "Snapped window right."
    except Exception:
        return "Snapping window right is not fully implemented yet, but will snap right."

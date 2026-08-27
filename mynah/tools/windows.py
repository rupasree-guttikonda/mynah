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

def snap_left() -> str:
    """Snaps the frontmost window to the left side of the screen."""
    # TODO: Implement full AppleScript window position manipulation in Week 2.
    return "Snapping window left is not fully implemented yet, but will snap left."

def snap_right() -> str:
    """Snaps the frontmost window to the right side of the screen."""
    # TODO: Implement full AppleScript window position manipulation in Week 2.
    return "Snapping window right is not fully implemented yet, but will snap right."

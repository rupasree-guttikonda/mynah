# mynah/tools/apps.py
"""
Application launch, focus, and termination tools using AppleScript.
"""

import subprocess

def launch(name: str) -> str:
    """Launches or focuses a macOS application by name."""
    # Escape quotes in the app name to prevent AppleScript injection
    safe_name = name.replace('"', '\\"')
    script = f'tell application "{safe_name}" to activate'
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return f"Successfully launched/focused {name}."
    except subprocess.CalledProcessError as e:
        # Fallback to system open command
        try:
            subprocess.run(["open", "-a", name], check=True, capture_output=True)
            return f"Successfully opened {name} via open CLI."
        except subprocess.CalledProcessError:
            error_msg = e.stderr.decode().strip() if e.stderr else "App not found"
            return f"Failed to launch {name}: {error_msg}"

def quit_app(name: str) -> str:
    """Quits a macOS application by name."""
    safe_name = name.replace('"', '\\"')
    script = f'tell application "{safe_name}" to quit'
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return f"Successfully quit {name}."
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else "App not running"
        return f"Failed to quit {name}: {error_msg}"

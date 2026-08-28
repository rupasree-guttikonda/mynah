# mynah/scheduler/launchd.py
"""
macOS launchd helper to schedule the nightly compaction job.
"""

import os
import sys
import subprocess

PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/com.mynah.compaction.plist")

def register_compaction_job() -> str:
    """
    Generates and registers the macOS launchd plist file to run compaction
    every night at 11:59 PM.
    """
    python_exec = sys.executable
    workspace_dir = os.getcwd()
    run_py = os.path.join(workspace_dir, "run.py")
    
    log_dir = os.path.expanduser("~/.gemini/antigravity-ide/logs")
    os.makedirs(log_dir, exist_ok=True)
    stdout_log = os.path.join(log_dir, "mynah_compaction_stdout.log")
    stderr_log = os.path.join(log_dir, "mynah_compaction_stderr.log")
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mynah.compaction</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exec}</string>
        <string>{run_py}</string>
        <string>--compact</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>59</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>{workspace_dir}</string>
    <key>StandardOutPath</key>
    <string>{stdout_log}</string>
    <key>StandardErrorPath</key>
    <string>{stderr_log}</string>
</dict>
</plist>
"""
    try:
        os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
        with open(PLIST_PATH, "w") as f:
            f.write(plist_content)
            
        # Unload if already loaded to avoid errors
        subprocess.run(["/bin/launchctl", "unload", PLIST_PATH], capture_output=True)
        # Load and write
        res = subprocess.run(["/bin/launchctl", "load", "-w", PLIST_PATH], capture_output=True, text=True)
        if res.returncode == 0:
            return f"Successfully registered compaction launchd job at {PLIST_PATH}"
        else:
            return f"Failed to register launchd job: {res.stderr.strip()}"
    except Exception as e:
        return f"Launchd scheduling error: {str(e)}"

# mynah/safety/kill_switch.py
"""
Global kill switch: a system-wide hotkey that immediately halts any
in-flight speech output and registered subprocesses, regardless of
which app currently has focus.
"""

import subprocess
import threading

try:
    from pynput import keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False


class GlobalKillSwitch:
    """
    Listens for a global hotkey (default: Cmd+Shift+K) system-wide and,
    when triggered, stops audio output and any registered subprocesses.
    """

    def __init__(self, hotkey: str = "<cmd>+<shift>+k"):
        self.hotkey = hotkey
        self.triggered = threading.Event()
        self._processes_to_kill = []
        self._listener = None
        self._on_trigger_callbacks = []

    def register_process(self, proc: subprocess.Popen):
        """Register a running subprocess (e.g. a 'say' or ollama call) to be killed on trigger."""
        self._processes_to_kill.append(proc)

    def on_trigger(self, callback):
        """Register a callback to run when the kill switch fires."""
        self._on_trigger_callbacks.append(callback)

    def trigger(self):
        """Actually perform the kill: stop audio, kill registered subprocesses, fire callbacks."""
        self.triggered.set()

        try:
            subprocess.run(["killall", "say"], capture_output=True)
        except Exception:
            pass

        for proc in self._processes_to_kill:
            try:
                if proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass
        self._processes_to_kill.clear()

        for cb in self._on_trigger_callbacks:
            try:
                cb()
            except Exception:
                pass

    def reset(self):
        """Clear the triggered flag so the system can resume normal operation."""
        self.triggered.clear()

    def start(self):
        """Start listening for the global hotkey in the background."""
        if not HAS_PYNPUT:
            raise RuntimeError("pynput is required for the global kill switch hotkey")

        hotkey_listener = keyboard.GlobalHotKeys({self.hotkey: self.trigger})
        hotkey_listener.start()
        self._listener = hotkey_listener

    def stop(self):
        """Stop listening for the hotkey."""
        if self._listener:
            self._listener.stop()
            self._listener = None
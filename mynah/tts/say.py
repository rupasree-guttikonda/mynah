# mynah/tts/say.py
"""
Text-to-Speech wrapper using native macOS 'say' command with streaming background support.
"""

import sys
import subprocess
import asyncio
import queue
import threading

class TextToSpeech:
    """
    Non-blocking and synchronous wrappers around macOS native 'say' command with streaming queue.
    """

    def __init__(self, voice: str = "Samantha", rate: int = 185):
        self.voice = voice
        self.rate = rate
        self.speech_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _speech_worker(self):
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            self.speak_sync(text)
            self.speech_queue.task_done()

    def queue_speech(self, text: str):
        """Queues text to be spoken sequentially in the background."""
        text = text.strip()
        if text:
            import re
            # Split by punctuation followed by space or newline
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for sentence in sentences:
                s = sentence.strip()
                if s:
                    self.speech_queue.put(s)

    def clear_queue(self):
        """Clears all queued speech items."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

    def stop(self):
        """Stops current speech output and clears queue."""
        self.clear_queue()
        if sys.platform == "darwin":
            subprocess.run(["killall", "say"], capture_output=True)

    def speak(self, text: str) -> bool:
        """Alias for queue_speech for compatibility."""
        self.queue_speech(text)
        return True

    def speak_sync(self, text: str) -> bool:
        """
        Speak text synchronously using macOS say command.
        """
        if not text or sys.platform != "darwin":
            print(f"[TTS Output]: {text}")
            return True

        try:
            subprocess.run(["say", "-v", self.voice, "-r", str(self.rate), text], check=True)
            return True
        except Exception:
            try:
                subprocess.run(["say", text], check=True)
                return True
            except Exception:
                return False

    async def speak_async(self, text: str) -> bool:
        """
        Speak text asynchronously using asyncio subprocess.
        """
        if not text or sys.platform != "darwin":
            print(f"[TTS Output]: {text}")
            return True

        try:
            proc = await asyncio.create_subprocess_exec(
                "say", "-v", self.voice, "-r", str(self.rate), text
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return self.speak_sync(text)

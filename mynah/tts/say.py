# mynah/tts/say.py
"""
Text-to-Speech wrapper using native macOS 'say' command.
"""

import sys
import subprocess
import asyncio


class TextToSpeech:
    """
    Non-blocking and synchronous wrappers around macOS native 'say' command.
    """

    def __init__(self, voice: str = "Samantha", rate: int = 185):
        self.voice = voice
        self.rate = rate

    def speak(self, text: str) -> bool:
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
            return self.speak(text)

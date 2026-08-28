# mynah/stt/streaming.py
"""
Streaming-style STT: periodically re-transcribes a sliding window of
recently captured audio, rather than waiting for the full utterance to
finish before transcribing anything.

Honest scope note: mlx-whisper doesn't support true incremental decoding
(refining one in-progress hypothesis token by token). This is the
realistic version of "streaming" achievable here: transcribe overlapping
windows on a fixed interval, treating each new transcription as the
latest, most complete guess. It reduces time-to-first-partial-result,
but re-does work each interval rather than truly incrementally decoding.
"""

import time
import threading
from typing import Callable, Optional

from mynah.stt.whisper import SpeechToText


class StreamingTranscriber:
    """
    Periodically transcribes the last `window_seconds` of audio from a
    ring buffer, calling `on_partial` with each new transcription.
    """

    def __init__(
        self,
        ring_buffer,
        stt: Optional[SpeechToText] = None,
        window_seconds: float = 3.0,
        interval_seconds: float = 1.0,
    ):
        self.ring_buffer = ring_buffer
        self.stt = stt or SpeechToText()
        self.window_seconds = window_seconds
        self.interval_seconds = interval_seconds
        self._running = False
        self._thread = None
        self.latest_text = ""

    def start(self, on_partial: Callable[[str], None]):
        """Start the periodic transcription loop in a background thread."""
        self._running = True

        def loop():
            while self._running:
                audio = self.ring_buffer.get_last_n_seconds(self.window_seconds)
                if len(audio) > 0:
                    text, _ = self.stt.transcribe(audio)
                    if text and text != self.latest_text:
                        self.latest_text = text
                        on_partial(text)
                time.sleep(self.interval_seconds)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the periodic transcription loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

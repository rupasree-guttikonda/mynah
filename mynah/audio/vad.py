# mynah/audio/vad.py
"""
Energy and zero-crossing rate Voice Activity Detector (VAD) for 16kHz PCM audio.
Separates speech frames from background silence.
"""

import numpy as np
from typing import List


class VoiceActivityDetector:
    """
    Detects voice activity in 16kHz float32 PCM audio arrays.
    """

    def __init__(self, energy_threshold: float = 0.015, frame_duration_ms: float = 30.0, sample_rate: int = 16000):
        self.energy_threshold = energy_threshold
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))

    def is_speech(self, float32_samples: np.ndarray) -> bool:
        """
        Returns True if the audio chunk exceeds the energy threshold.
        """
        if len(float32_samples) == 0:
            return False

        rms_energy = np.sqrt(np.mean(float32_samples**2))
        return bool(rms_energy >= self.energy_threshold)

    def extract_speech_segments(self, float32_samples: np.ndarray) -> List[np.ndarray]:
        """
        Splits continuous audio into speech segments by filtering out silence frames.
        """
        if len(float32_samples) == 0:
            return []

        segments = []
        current_segment = []

        for i in range(0, len(float32_samples), self.frame_size):
            frame = float32_samples[i : i + self.frame_size]
            if len(frame) < self.frame_size:
                continue

            if self.is_speech(frame):
                current_segment.extend(frame)
            elif current_segment:
                segments.append(np.array(current_segment, dtype=np.float32))
                current_segment = []

        if current_segment:
            segments.append(np.array(current_segment, dtype=np.float32))

        return segments

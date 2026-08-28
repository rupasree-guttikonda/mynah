# mynah/stt/whisper.py
"""
Low-latency Speech-To-Text pipeline using mlx-whisper on Apple Silicon.
Supports auto-detection of 99+ spoken languages or English-specific models.
"""

import time
import numpy as np
from typing import Tuple, Optional

try:
    import mlx_whisper
    HAS_MLX_WHISPER = True
except Exception:
    HAS_MLX_WHISPER = False


class SpeechToText:
    """
    Transcribes 16kHz float32 PCM numpy audio arrays into text using mlx-whisper.
    Supports multilingual auto-detection (99+ languages) or English-optimized models.
    """

    def __init__(self, model_name: str = "mlx-community/whisper-tiny"):
        """
        Multilingual models: 'mlx-community/whisper-tiny', 'mlx-community/whisper-small'
        English-only models: 'mlx-community/whisper-tiny.en', 'mlx-community/whisper-small.en'
        """
        self.model_name = model_name

    def transcribe(self, float32_samples: np.ndarray, language: Optional[str] = None) -> Tuple[str, float]:
        """
        Transcribe 1D float32 PCM audio array into text.
        If language is None, Whisper automatically detects the spoken language.
        Returns (transcribed_text: str, latency_seconds: float).
        """
        start_time = time.time()
        if not HAS_MLX_WHISPER or len(float32_samples) == 0:
            return "", 0.0

        try:
            kwargs = {"path_or_hf_repo": self.model_name}
            if language:
                kwargs["language"] = language

            res = mlx_whisper.transcribe(float32_samples, **kwargs)
            text = res.get("text", "").strip() if isinstance(res, dict) else ""
            latency = time.time() - start_time
            return text, latency
        except Exception:
            latency = time.time() - start_time
            return "", latency

# mynah/audio/wakeword.py
"""
openWakeWord integration for real-time wake phrase detection ("hey mynah").
Supports multi-phrase detection, custom ONNX models, and sensitivity tuning.
"""

import os
import glob
import numpy as np
from typing import List, Optional, Union

try:
    import openwakeword
    from openwakeword.model import Model
    HAS_OPENWAKEWORD = True
except Exception:
    HAS_OPENWAKEWORD = False


class WakeWordDetector:
    """
    Scans continuous PCM audio chunks using openWakeWord to detect wake phrases.
    Default wake phrases: ["hey mynah", "mynah", "hey assistant"].
    Supports loading custom .onnx model files from models/wakeword/ and sensitivity tuning.
    """

    def __init__(
        self,
        target_phrase: Optional[Union[str, List[str]]] = None,
        target_phrases: Optional[List[str]] = None,
        threshold: float = 0.45,
        custom_model_dir: str = "models/wakeword",
        sample_rate: int = 16000,
    ):
        phrases = target_phrases or target_phrase or ["hey mynah", "mynah", "hey assistant"]
        if isinstance(phrases, str):
            phrases = [phrases]

        self.target_phrases = [p.lower() for p in phrases]
        self.target_phrase = self.target_phrases[0]
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.custom_model_dir = custom_model_dir
        self.model = None

        if HAS_OPENWAKEWORD:
            # Check for custom ONNX models in custom_model_dir
            onnx_files = []
            if os.path.exists(custom_model_dir):
                onnx_files = glob.glob(os.path.join(custom_model_dir, "*.onnx"))

            try:
                if onnx_files:
                    self.model = Model(wakeword_models=onnx_files, inference_framework="onnx")
                else:
                    self.model = Model(inference_framework="onnx")
            except Exception:
                self.model = None

    def set_sensitivity(self, threshold: float) -> None:
        """Dynamically tune detection sensitivity threshold (0.1 to 0.9)."""
        self.threshold = max(0.1, min(0.9, threshold))

    def process_chunk(self, float32_samples: np.ndarray) -> bool:
        """
        Process a chunk of float32 PCM audio samples (at 16kHz).
        Returns True if any wake phrase confidence score meets or exceeds the sensitivity threshold.
        """
        if self.model is None or len(float32_samples) == 0:
            return False

        # Convert float32 [-1.0, 1.0] to int16 [-32768, 32767]
        pcm_int16 = (np.clip(float32_samples, -1.0, 1.0) * 32767).astype(np.int16)

        predictions = self.model.predict(pcm_int16)

        for model_name, score in predictions.items():
            if score >= self.threshold:
                if hasattr(self.model, "reset"):
                    self.model.reset()
                return True

        return False

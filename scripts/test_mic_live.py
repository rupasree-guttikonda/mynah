#!/usr/bin/env python3
"""
Diagnostic live microphone & wake word scoring monitor.
Visualizes real-time microphone volume (RMS) and raw openWakeWord detection scores.
"""

import os
import sys
import time

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import sounddevice as sd
from mynah.audio.wakeword import WakeWordDetector
from mynah.config import MYNAH_WAKEWORD_THRESHOLD

def main():
    print("==================================================")
    print(" Mynah Microphone & 'hey mynah' Live Diagnostics  ")
    print("==================================================")
    
    # Initialize wake word detector
    detector = WakeWordDetector(threshold=MYNAH_WAKEWORD_THRESHOLD)
    if detector.model is None:
        print("ERROR: WakeWord model failed to load. Check models/wakeword/ folder.")
        sys.exit(1)
        
    print(f"Loaded models: {list(detector.model.models.keys())}")
    print(f"Sensitivity threshold: {detector.threshold:.2f}")
    print("Speak into your microphone now. Say 'hey mynah' naturally.")
    print("Press Ctrl+C to stop.\n")
    
    CHUNK_SIZE = 1280  # 80ms at 16kHz
    SAMPLE_RATE = 16000
    
    # Track max score in the last 1 second
    recent_scores = []
    
    def audio_callback(indata, frames, time_info, status):
        nonlocal recent_scores
        samples = indata[:, 0].copy()
        
        # Calculate RMS volume
        rms = np.sqrt(np.mean(samples ** 2))
        vol_bars = int(min(20, rms * 100))
        bar_str = "█" * vol_bars + "░" * (20 - vol_bars)
        
        # Predict wake word score
        pcm_int16 = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
        predictions = detector.model.predict(pcm_int16)
        
        # Get highest score across models
        top_score = max(predictions.values()) if predictions else 0.0
        model_name = max(predictions, key=predictions.get) if predictions else "none"
        
        status_tag = ""
        if top_score >= detector.threshold:
            status_tag = f"  >>> [TRIGGERED: {model_name.upper()} ({top_score:.2f})] <<<"
            
        sys.stdout.write(f"\rMic Vol: [{bar_str}] {rms:0.3f} | '{model_name}': {top_score:0.3f}{status_tag}   ")
        sys.stdout.flush()

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=CHUNK_SIZE, callback=audio_callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic monitor stopped.")

if __name__ == "__main__":
    main()

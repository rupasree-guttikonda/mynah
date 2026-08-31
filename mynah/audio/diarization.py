# mynah/audio/diarization.py
"""
Basic speaker turn/segmentation.

Honest scope note: this does NOT do real speaker diarization (no voice
embeddings, no speaker identity recognition/re-identification). It only
detects likely speaker CHANGES between consecutive speech segments using
pause boundaries (VAD) plus a simple pitch-shift heuristic. It cannot
tell you "this is the same person from 5 minutes ago" - only "this
segment sounds like a different voice than the immediately preceding
one." Real diarization needs a trained speaker-embedding model
(e.g. pyannote, resemblyzer), which is out of scope here.
"""

import numpy as np
from typing import List, Dict

from mynah.audio.vad import VoiceActivityDetector


def _estimate_pitch(segment: np.ndarray, sample_rate: int = 16000,
                     min_hz: float = 75.0, max_hz: float = 400.0) -> float:
    """
    Rough fundamental frequency estimate via autocorrelation. Returns 0.0
    if the segment is too quiet/short to get a reliable estimate.
    """
    if len(segment) < sample_rate * 0.05:
        return 0.0

    segment = segment - np.mean(segment)
    if np.max(np.abs(segment)) < 1e-4:
        return 0.0

    corr = np.correlate(segment, segment, mode="full")
    corr = corr[len(corr) // 2:]

    min_lag = int(sample_rate / max_hz)
    max_lag = int(sample_rate / min_hz)
    if max_lag >= len(corr):
        return 0.0

    search_range = corr[min_lag:max_lag]
    if len(search_range) == 0:
        return 0.0

    peak_lag = np.argmax(search_range) + min_lag
    if peak_lag == 0:
        return 0.0

    return sample_rate / peak_lag


def segment_by_speaker_turns(
    float32_samples: np.ndarray,
    sample_rate: int = 16000,
    pitch_change_threshold_hz: float = 40.0,
) -> List[Dict]:
    """
    Splits audio into speech segments (via VAD) and assigns a sequential
    speaker label to each, incrementing the label whenever the estimated
    pitch shifts by more than `pitch_change_threshold_hz` from the
    previous segment. This is a turn-detection heuristic, not true
    speaker identification.
    """
    vad = VoiceActivityDetector(sample_rate=sample_rate)
    segments = vad.extract_speech_segments(float32_samples)

    results = []
    speaker_num = 1
    prev_pitch = None

    for seg in segments:
        pitch = _estimate_pitch(seg, sample_rate=sample_rate)

        if prev_pitch is not None and pitch > 0 and prev_pitch > 0:
            if abs(pitch - prev_pitch) > pitch_change_threshold_hz:
                speaker_num += 1

        results.append({
            "speaker": f"Speaker {speaker_num}",
            "audio": seg,
            "pitch_hz": round(pitch, 1),
        })

        if pitch > 0:
            prev_pitch = pitch

    return results

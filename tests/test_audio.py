import pytest
import numpy as np
from mynah.audio import (
    AudioRingBuffer,
    AudioCaptureManager,
    WakeWordDetector,
    check_microphone_permission,
    request_microphone_permission,
)
from mynah.stt import SpeechToText
from mynah.tts import TextToSpeech

def test_audio_device_module():
    import sounddevice as sd
    assert hasattr(sd, "query_devices")

def test_stt_whisper_module():
    import mlx_whisper
    assert hasattr(mlx_whisper, "transcribe")

def test_ring_buffer_basic_append_and_get():
    buf = AudioRingBuffer(capacity_seconds=1.0, sample_rate=100)
    assert buf.capacity == 100
    assert len(buf.get_all()) == 0

    data = np.arange(50, dtype=np.float32)
    buf.append(data)
    assert buf.size == 50

    retrieved = buf.get_last_n_seconds(0.3)  # Should get 30 samples
    assert len(retrieved) == 30
    np.testing.assert_array_equal(retrieved, data[20:50])

def test_ring_buffer_wraparound():
    buf = AudioRingBuffer(capacity_seconds=1.0, sample_rate=100)
    buf.append(np.arange(80, dtype=np.float32))
    buf.append(np.arange(100, 150, dtype=np.float32))

    assert buf.size == 100
    all_data = buf.get_all()
    assert len(all_data) == 100
    expected = np.concatenate([np.arange(30, 80, dtype=np.float32), np.arange(100, 150, dtype=np.float32)])
    np.testing.assert_array_equal(all_data, expected)

def test_ring_buffer_overflow_chunk():
    buf = AudioRingBuffer(capacity_seconds=1.0, sample_rate=100)
    data = np.arange(150, dtype=np.float32)
    buf.append(data)
    assert buf.size == 100
    all_data = buf.get_all()
    np.testing.assert_array_equal(all_data, np.arange(50, 150, dtype=np.float32))

def test_ring_buffer_clear():
    buf = AudioRingBuffer(capacity_seconds=1.0, sample_rate=100)
    buf.append(np.ones(50, dtype=np.float32))
    assert buf.size == 50
    buf.clear()
    assert buf.size == 0
    assert len(buf.get_all()) == 0

def test_audio_capture_manager_init():
    manager = AudioCaptureManager(sample_rate=16000, capacity_seconds=2.0)
    assert not manager.is_active
    assert manager.ring_buffer.capacity == 32000

def test_check_microphone_permission():
    status = check_microphone_permission()
    assert isinstance(status, bool)

def test_wakeword_detector_init():
    detector = WakeWordDetector(target_phrase="hey mynah", threshold=0.5)
    assert detector.target_phrase == "hey mynah"
    # Silence float32 chunk processing
    result = detector.process_chunk(np.zeros(1280, dtype=np.float32))
    assert isinstance(result, bool)

def test_speech_to_text_empty():
    stt = SpeechToText()
    text, latency = stt.transcribe(np.array([], dtype=np.float32))
    assert text == ""
    assert isinstance(latency, float)

def test_text_to_speech_init():
    tts = TextToSpeech()
    assert hasattr(tts, "speak")
    assert hasattr(tts, "speak_async")

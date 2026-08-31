# mynah/audio/capture.py
"""
Audio capture module using PyObjC AVFoundation mic permission checks and
sounddevice streaming into a thread-safe sliding numpy ring buffer.
"""

import sys
import threading
import numpy as np
import sounddevice as sd

try:
    import objc
    from AVFoundation import (
        AVCaptureDevice,
        AVMediaTypeAudio,
        AVAuthorizationStatusAuthorized,
        AVAuthorizationStatusDenied,
        AVAuthorizationStatusRestricted,
        AVAuthorizationStatusNotDetermined,
    )
    HAS_PYOBJC = True
except ImportError:
    HAS_PYOBJC = False


def check_microphone_permission() -> bool:
    """
    Check macOS microphone authorization status using PyObjC AVFoundation.
    Returns True if authorized or non-macOS system, False otherwise.
    """
    if sys.platform != "darwin" or not HAS_PYOBJC:
        return True
    status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)
    return status == AVAuthorizationStatusAuthorized


def request_microphone_permission() -> bool:
    """
    Request macOS microphone permission if status is NotDetermined.
    Returns True if permission granted or already authorized, False otherwise.
    """
    if sys.platform != "darwin" or not HAS_PYOBJC:
        return True
    status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)
    if status == AVAuthorizationStatusAuthorized:
        return True
    if status == AVAuthorizationStatusNotDetermined:
        result = [False]
        event = threading.Event()

        def handler(granted: bool):
            result[0] = granted
            event.set()

        AVCaptureDevice.requestAccessForMediaType_completionHandler_(AVMediaTypeAudio, handler)
        event.wait(timeout=10.0)
        return result[0]
    return False


class AudioRingBuffer:
    """
    Thread-safe circular numpy audio ring buffer for 16kHz float32 PCM samples.
    """

    def __init__(self, capacity_seconds: float = 5.0, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.capacity = int(capacity_seconds * sample_rate)
        self.buffer = np.zeros(self.capacity, dtype=np.float32)
        self.write_pos = 0
        self.size = 0
        self.lock = threading.RLock()

    def append(self, samples: np.ndarray) -> None:
        """
        Append a 1D float32 numpy audio sample chunk into the ring buffer.
        """
        samples = np.asarray(samples, dtype=np.float32).flatten()
        n = len(samples)
        if n == 0:
            return

        with self.lock:
            if n >= self.capacity:
                self.buffer[:] = samples[-self.capacity :]
                self.write_pos = 0
                self.size = self.capacity
            else:
                end_pos = (self.write_pos + n) % self.capacity
                if self.write_pos + n <= self.capacity:
                    self.buffer[self.write_pos : self.write_pos + n] = samples
                else:
                    first_part = self.capacity - self.write_pos
                    self.buffer[self.write_pos :] = samples[:first_part]
                    self.buffer[: n - first_part] = samples[first_part:]
                self.write_pos = end_pos
                self.size = min(self.capacity, self.size + n)

    def get_last_n_seconds(self, seconds: float) -> np.ndarray:
        """
        Retrieve the last N seconds of recorded audio samples as a 1D float32 array.
        """
        requested_samples = int(seconds * self.sample_rate)
        with self.lock:
            n = min(requested_samples, self.size)
            if n == 0:
                return np.array([], dtype=np.float32)
            start_pos = (self.write_pos - n) % self.capacity
            if start_pos + n <= self.capacity:
                return self.buffer[start_pos : start_pos + n].copy()
            else:
                first_part = self.capacity - start_pos
                res = np.empty(n, dtype=np.float32)
                res[:first_part] = self.buffer[start_pos:]
                res[first_part:] = self.buffer[: n - first_part]
                return res

    def get_all(self) -> np.ndarray:
        """
        Get all currently stored audio samples.
        """
        with self.lock:
            if self.size == 0:
                return np.array([], dtype=np.float32)
            return self.get_last_n_seconds(self.size / self.sample_rate)

    def clear(self) -> None:
        """
        Clear all stored buffer contents.
        """
        with self.lock:
            self.buffer.fill(0)
            self.write_pos = 0
            self.size = 0


class AudioCaptureManager:
    """
    Manages real-time microphone stream input using sounddevice, feeding samples
    continuously into an AudioRingBuffer.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1, capacity_seconds: float = 5.0):
        self.sample_rate = sample_rate
        self.channels = channels
        self.ring_buffer = AudioRingBuffer(capacity_seconds=capacity_seconds, sample_rate=sample_rate)
        self.stream = None
        self._is_active = False

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags):
        samples = indata[:, 0].copy()
        self.ring_buffer.append(samples)

    def start(self) -> None:
        if self._is_active:
            return
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._audio_callback,
        )
        self.stream.start()
        self._is_active = True

    def stop(self) -> None:
        if not self._is_active:
            return
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

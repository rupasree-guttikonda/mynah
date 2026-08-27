# Mynah Tasks & Roadmap

## 🎤 Dev A Tasks (Systems & Audio)

### Week 1 — Audio Pipeline & Systems Shell
- [x] **DEV-A-101: Mic Permissions & PyObjC Audio Capture Ring Buffer**
  - Implement PyObjC audio recording loop with continuous ring buffer in `mynah/audio/capture.py`.
  - Add macOS microphone permission request & validation helper.
- [ ] **DEV-A-102: openWakeWord Integration**
  - Integrate `openWakeWord` engine to listen on the audio ring buffer in `mynah/audio/wakeword.py`.
  - Tune sensitivity thresholds for reliable wake phrase detection.
- [ ] **DEV-A-103: STT Pipeline (`mlx-whisper`)**
  - Implement `mynah/stt/whisper.py` using `mlx-whisper` for low-latency Apple Silicon transcription.
  - Benchmark model sizes (`tiny.en` vs `small.en`) for latency and accuracy trade-offs.
- [ ] **DEV-A-104: Native macOS TTS Wrapper**
  - Implement `mynah/tts/say.py` wrapping the macOS native `say` command.
- [ ] **DEV-A-105: SQLite Metrics & Turns Logging**
  - Implement `mynah/log/audit.py` to create the `turns` table and log execution latencies/costs.

---

## 🧠 Dev B Tasks (Logic & Brain)

### Week 1 — Core App Loop & Tool Registry
- [ ] **DEV-B-101: Application Shell & Event Loop**
  - Implement main async loop in `mynah.py`.
- [ ] **DEV-B-102: Tier 0 Regex Router**
  - Parse `rules/instant.yaml` and execute instant regex matches.
- [ ] **DEV-B-103: System Tool Handlers**
  - Expand execution wrappers in `mynah/tools/` (`apps.py`, `windows.py`, `files.py`).

# Mynah Tasks & Roadmap

## 🎤 Dev A Tasks (Systems & Audio)

### Week 1 — Audio Pipeline & Systems Shell
- [x] **DEV-A-101: Mic Permissions & PyObjC Audio Capture Ring Buffer**
- [x] **DEV-A-102: openWakeWord Integration ("hey mynah")**
- [x] **DEV-A-103: STT Pipeline (`mlx-whisper`)**
- [x] **DEV-A-104: Native macOS TTS Wrapper**
- [x] **DEV-A-105: End-to-End Audio & Router Integration**

### Week 2 — Memory Search & System Window Controls
- [x] **DEV-A-201: Ripgrep Vault Search & Recency Ranking**
- [x] **DEV-A-202: macOS Window Controls & Frontmost App Inspector**

### Weeks 3 & 4 — Local Brain Performance & Ollama Benchmarking
- [x] **DEV-A-301: Ollama & Local Model Performance Benchmarker**

### Week 5 — Latency Metrics & Daily Budget Guardrails
- [x] **DEV-A-501: Token Counter & Performance Latency Metrics**
- [x] **DEV-A-502: Daily Spend Limit Guardrail ($1.00 Threshold)**

### Week 6 — VAD & Continuous Meeting Recording
- [ ] **DEV-A-601: Voice Activity Detection (VAD) Speech Segmenter**
  - Implement energy-based acoustic VAD in `mynah/audio/vad.py` for speech/silence detection.
- [ ] **DEV-A-602: Speaker Segmentation Helper**
  - Implement timestamp-based speaker turn segmenter in `mynah/audio/diarization.py`.

### Week 7 — macOS Clipboard Inspector & System Tools
- [ ] **DEV-A-701: PyObjC NSPasteboard Clipboard Reader**
  - Implement native clipboard text reader in `mynah/tools/clipboard.py` using PyObjC `AppKit.NSPasteboard`.

### Week 8 — macOS Menu Bar UI & Global Kill Switch
- [ ] **DEV-A-801: Native PyObjC macOS Menu Bar Status Indicator**
  - Implement status bar menu item (`mynah/ui/menubar.py`) displaying status and daily spend.
- [ ] **DEV-A-802: Global Kill Switch**
  - Implement emergency stop signal handler (`mynah/safety/killswitch.py`) halting audio, models, and TTS.

### Week 9 — Audio Polish, Streaming STT & Power-Aware Rules
- [ ] **DEV-A-901: 500ms Sliding Window Streaming STT**
  - Implement streaming STT in `mynah/stt/streaming.py` for continuous live transcription.
- [ ] **DEV-A-902: macOS Power-Aware Battery Manager**
  - Implement battery state monitor in `mynah/router/power.py` using macOS IOKit APIs to unload local models on battery.

---

## 🧠 Dev B Tasks (Logic & Brain) — Completed (Weeks 1–5 Merged)
- [x] **DEV-B-101: Application Shell & Tool Registry**
- [x] **DEV-B-102: Tier 0 Regex Router & Rule Engine**
- [x] **DEV-B-201: Markdown Memory Vault & Quarantine Boundary Rules**
- [x] **DEV-B-301: Local Ollama Model Tool Schema & JSON Grammars**
- [x] **DEV-B-401: Context Injection (Active App, Identity & Conversation Turns)**
- [x] **DEV-B-501: Anthropic & OpenAI Cloud Escalation Client with Prompt Caching**

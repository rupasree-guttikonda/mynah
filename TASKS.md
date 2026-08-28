# Mynah Tasks & Roadmap

## 🎤 Dev A Tasks (Systems & Audio)

### Week 1 — Audio Pipeline & Systems Shell
- [x] **DEV-A-101: Mic Permissions & PyObjC Audio Capture Ring Buffer**
  - Implement PyObjC audio recording loop with continuous ring buffer in `mynah/audio/capture.py`.
  - Add macOS microphone permission request & validation helper.
- [x] **DEV-A-102: openWakeWord Integration ("hey mynah")**
  - Integrate `openWakeWord` engine to listen on the audio ring buffer in `mynah/audio/wakeword.py`.
  - Tune sensitivity thresholds for reliable wake phrase detection.
- [x] **DEV-A-103: STT Pipeline (`mlx-whisper`)**
  - Implement `mynah/stt/whisper.py` using `mlx-whisper` for low-latency Apple Silicon transcription.
  - Benchmark model sizes (`tiny.en` vs `small.en`) for latency and accuracy trade-offs.
- [x] **DEV-A-104: Native macOS TTS Wrapper**
  - Implement `mynah/tts/say.py` wrapping the macOS native `say` command.
- [x] **DEV-A-105: End-to-End Audio & Router Integration**
  - Connect audio capture -> wake word -> STT -> Router -> TTS -> SQLite audit log in `run.py` & `mynah.py`.

### Week 2 — Memory Search & System Window Controls
- [x] **DEV-A-201: Ripgrep Vault Search & Recency Ranking**
  - Implement `ripgrep` search integration in `mynah/tools/vault.py` with modified-time recency ranking.
- [x] **DEV-A-202: macOS Window Controls & Frontmost App Inspector**
  - Implement `get_frontmost_app_info()`, AppleScript window positioning (`snap_left`, `snap_right`) in `mynah/tools/windows.py`.

### Weeks 3 & 4 — Local Brain Performance & Ollama Benchmarking
- [x] **DEV-A-301: Ollama & Local Model Performance Benchmarker**
  - Implement token-generation throughput measurement (tokens/sec) and system RAM footprint profiler for Ollama.

### Week 5 — Latency Metrics & Daily Budget Guardrails
- [x] **DEV-A-501: Token Counter & Performance Latency Metrics**
  - Implement `tiktoken` token counter and latency profiler for STT, Route, and Exec steps in SQLite `turns` table.
- [x] **DEV-A-502: Daily Spend Limit Guardrail ($1.00 Threshold)**
  - Intercept cloud queries, calculate rolling daily spend from `turns` table, and enforce refusal when spend exceeds $1.00.

---

## 🧠 Dev B Tasks (Logic & Brain) — Completed (Weeks 1–5 Merged)
- [x] **DEV-B-101: Application Shell & Tool Registry**
- [x] **DEV-B-102: Tier 0 Regex Router & Rule Engine**
- [x] **DEV-B-201: Markdown Memory Vault & Quarantine Boundary Rules**
- [x] **DEV-B-301: Local Ollama Model Tool Schema & JSON Grammars**
- [x] **DEV-B-401: Context Injection (Active App, Identity & Conversation Turns)**
- [x] **DEV-B-501: Anthropic & OpenAI Cloud Escalation Client with Prompt Caching**

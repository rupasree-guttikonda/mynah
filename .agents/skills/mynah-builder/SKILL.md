---
name: mynah-builder
description: Guide and context for developing, testing, and verifying the Mynah local voice assistant.
---

# Mynah Build Skill

This skill assists developers in constructing, testing, and debugging the Mynah local voice assistant.

## 🛠️ Repository Layout Reference
When writing new modules, follow this layout:
- `mynah/audio/`: PyObjC audio capture, VAD, ring buffer
- `mynah/stt/`: whisper.cpp wrapper, streaming buffer
- `mynah/router/`: rules table, Ollama/Claude clients, confidence scores
- `mynah/tools/`: apps.py, windows.py, files.py, vault.py, clipboard.py, systems.py
- `mynah/memory/`: vault I/O, quarantine rules, nightly compaction scripts
- `mynah/tts/`: macOS `say` wrapper, sentence streaming queue
- `mynah/safety/`: confirmation gate, budget/token limits, kill switch
- `mynah/log/`: SQLite audit logs
- `rules/instant.yaml`: regex rules for Tier 0
- `mynah.py`: Main process thread loop

---

## 🏃 Testing & Verification Commands

### 1. Audio Loop Mocking
To test the router and execution layers without constantly speaking:
```bash
python -m unittest tests/test_router.py
```
Or write a simple mock shell command:
```bash
python mynah.py --mock-text "open Slack"
```

### 2. SQLite Metrics Verification
To check latency and cost of recent runs:
```sql
sqlite3 audit.db "SELECT ts, transcript, matched_tier, tool, cost_usd, latency_route FROM turns ORDER BY ts DESC LIMIT 5;"
```

### 3. Ollama Connection & Throughput Test
Verify the local Qwen instance performance:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:8b-instruct-q4_K_M",
  "prompt": "Test connection"
}'
```

---

## 📋 Weekly Iteration Checklist
When the user asks to start a specific week, reference the plan in [4-Collaborative-Build-Plan.md](file:///Users/avr/Projects/mynah/4-Collaborative-Build-Plan.md):
1. **Week 1:** Setup skeleton, SQLite schema, audio ring buffer, openWakeWord, whisper.cpp, and first 10 simple rules.
2. **Week 2:** Markdown Vault, `vault.append` tool, `ripgrep` search, quarantine boundaries.
3. **Week 3-4:** Ollama tool constraints, Apple FM benchmark, context injection, and lazy loading.
4. **Week 5:** Claude client integration, confidence routing, token caps, and budget checks.
5. **Week 6-7:** Continuous transcription, diarization, nightly compaction, and clipboard action tools.
6. **Week 8-9:** Safety confirm gate, Global Kill Switch hotkey, menu bar indicators, and streaming TTS boundaries.


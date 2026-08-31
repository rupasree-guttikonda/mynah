# Handover — Dev A status (as of Aug 28, 2026)

## ⚠️ Read this before merging anything

Rupasree is away and unreachable for a bit. **Do not merge
`integration/audio-and-brain` into `dev-a/audio-pipeline` without
talking first** — it appears to be an independent full rebuild
(64 files, ~6,700 lines against empty `main`) that touches the same
files already fixed today on this branch (`wakeword.py`, `windows.py`,
`run.py`, `clipboard.py`). A blind merge could silently undo verified
fixes on either side. Also: the trained `hey_mynah.onnx` wake word
file does NOT appear to exist in that branch — confirmed via
`git ls-tree`, came back empty.

## ✅ Genuinely verified today (not just claimed — hand-tested, live)

- Mic permission check (real system dialog)
- Speech-to-text (mlx-whisper, real audio → correct text)
- Text-to-speech (real audio out, confirmed by ear)
- Vault append + search (real file, real search results)
- Window tools: get_time, set_volume, mute, unmute, frontmost app detection
- Window snap left/right — **found and fixed a false-success bug**
  (inner AppleScript try/catch was silently swallowing real failures)
- Ollama/Qwen benchmark (real tokens/sec, real RAM detection)
- Token counting (tiktoken)
- Daily budget guardrail — **found and fixed a fail-open bug** (a broken
  DB check used to silently permit unlimited spend; now fails closed)
- VAD (voice activity detection) — real energy-based detection, tested
  against real silence vs real speech recordings
- Clipboard read/write — **built from scratch**, was an empty stub
  despite being marked "complete"; verified with real copy/paste
- Global kill switch (Cmd+Shift+K) — **built from scratch**; verified it
  stops active speech mid-sentence AND fires while a different app has
  focus (genuine system-wide hotkey)
- Menu bar app (rumps) — **built from scratch**; verified dropdown,
  mute toggle, live spend display, clean quit
- Streaming STT (sliding-window re-transcription) — built and verified
  live; NOT true incremental decoding, documented as such in the code
- Basic speaker turn detection (VAD + pitch-shift heuristic) — **built
  from scratch**; NOT real diarization (no voice embeddings), documented
  as such; verified it detects a deliberate pitch change

## ❌ Confirmed genuinely missing (not stubs, not bugs — never existed)

- Real echo cancellation (genuinely hard, needs native Swift/ObjC Voice
  Processing AudioUnit — flagged as realistically out of scope for a
  Python-only build)

## 🐛 Known issues found in run.py, not yet fixed (flagging for Dev B)

- `turn_data["frontmost_app"] = "Terminal"` is HARDCODED — never calls
  the real, verified `windows.get_frontmost_app_info()`. Every audit
  log entry says "Terminal" regardless of reality.
- `matched_tier` (0/1/2) is computed correctly in `route_and_execute()`
  but is silently discarded — the `turns` table in `audit.db` has no
  `matched_tier` column at all. This means the tier-routing metric
  (the most resume-relevant piece of this whole project) has never
  actually been persisted, despite being computed every turn.
- `brain.py`: qwen3 is a "thinking" model — raw output includes a full
  "Thinking... Okay, the user is asking..." block before the real
  answer. Needs stripping before TTS or the assistant will literally
  speak its internal reasoning out loud.

## Where things are

- Branch: `dev-a/audio-pipeline`, up to date, all of today's work
  pushed (`37d2c00` is the latest commit as of this handover).
- `main` is still empty — nothing has been merged there yet.

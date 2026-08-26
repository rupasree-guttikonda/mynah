# Mynah — Technical Design

Document 2 of 3
Target: MacBook Air M4, 16GB, macOS 26

---

## 1. Architecture

Everything below runs in a single Python process. No IPC, no second runtime, no external agent framework. The whole point is that the path from microphone to action is a chain of function calls.

```
                      ┌──────────────┐
   microphone ──────► │  wake word   │  openWakeWord, ~50MB, always on
                      └──────┬───────┘
                             ▼
                      ┌──────────────┐
                      │     STT      │  whisper.cpp small.en, streaming
                      └──────┬───────┘
                             ▼
                      ┌──────────────┐
                      │    router    │  rules first, then local model
                      └──┬────┬────┬─┘
              ┌──────────┘    │    └──────────┐
              ▼               ▼               ▼
      ┌───────────────┐ ┌───────────┐ ┌──────────────┐
      │    Tier 0     │ │  Tier 1   │ │   Tier 2     │
      │ pattern match │ │ local 8B  │ │  cloud API   │
      │  no model     │ │ tool call │ │  escalation  │
      │  ~70%         │ │  ~25%     │ │   ~5%        │
      └───────┬───────┘ └─────┬─────┘ └──────┬───────┘
              └───────────────┼──────────────┘
                              ▼
                    ┌──────────────────┐
                    │  tool executor   │  confirmation gate
                    └────────┬─────────┘
                             ▼
              ┌──────────────┴──────────────┐
              ▼                             ▼
       ┌─────────────┐              ┌──────────────┐
       │ vault (md)  │              │  TTS (say)   │
       └─────────────┘              └──────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   audit log      │  every turn, SQLite
                    └──────────────────┘
```

The audit log is not an afterthought. It is the training data for v2.0 and the enforcement point for the spend ceiling.

---

## 2. The three tiers

### Tier 0 — no model
A YAML table of patterns mapped to tools. Regex matching, direct execution.

```yaml
- pattern: "open (.+)"
  tool: apps.launch
  args: {name: "$1"}

- pattern: "(note|remember) (that )?(.+)"
  tool: vault.append
  args: {text: "$3"}

- pattern: "work mode"
  tool: focus.activate
  args: {profile: work}
```

Should cover the majority of daily traffic. Zero cost, sub-100ms, works offline. Growing this table automatically is the point of v2.0.

### Tier 1 — local model
Fires only when Tier 0 misses. Maps novel phrasing onto an existing tool.

Use grammar-constrained decoding (GBNF in llama.cpp, or Ollama's native tools API). This forces valid JSON at the token level so the model physically cannot narrate around the schema. It is the difference between a model that works and one that fails 15% of the time.

**Always inject three things into the router context:**
1. The frontmost application and window title. A large prior on intent — "send it" means different things in Mail and Terminal.
2. The stable identity block from the vault, under 500 tokens.
3. The last two turns, for pronoun resolution.

### Tier 2 — cloud
Triggered by: explicit knowledge questions, low local confidence, requests needing current information, or long-context synthesis.

- Haiku by default, Sonnet on low confidence
- Cache the system prompt and tool schemas; byte-identical every call
- Stream the response
- Hard cap at 8,000 tokens per request
- Refuse when the daily ceiling is hit, and say so out loud

---

## 3. Technology stack

### Audio

| Technology | Role | Cost | Why |
|---|---|---|---|
| openWakeWord | Wake word detection | Free | ONNX, custom phrase, ~50MB, negligible CPU |
| whisper.cpp `small.en` Q5 | Speech to text | Free | C binary, Metal-accelerated, streaming, no Python runtime |
| macOS `say` | Speech out | Free | Premium Siri-family voices installed, zero latency |
| Voice Processing AudioUnit | Echo cancellation | Free | Enables barge-in without the mic hearing the assistant |

### Models

| Technology | Role | Footprint | Why |
|---|---|---|---|
| Qwen3 8B Q4_K_M | Local reasoning and tool calling | 5GB | Native tool-call tokens, strong structured output |
| Qwen3 4B Q4 | Fallback under memory pressure | 2.5GB | Same family, half the size |
| Ollama or MLX | Inference runtime | — | Ollama for the tools API, MLX for raw Apple Silicon speed |
| GBNF grammars | Constrained decoding | — | Schema-valid JSON guaranteed at token level |
| Claude API | Escalation | ~$1–3/mo | Haiku default, Sonnet on low confidence |

**Quantisation floor: Q4_K_M.** Q3 and Q2 degrade tool-call reliability before conversational quality, so the model keeps sounding fine while silently producing malformed JSON.

### Memory and retrieval

| Technology | Role | Why |
|---|---|---|
| Markdown + YAML frontmatter | Storage format | Portable, human-readable, no lock-in |
| Obsidian | Human-facing viewer | Views the files; not a dependency |
| ripgrep | Primary search | Beats vector search at personal scale on latency and precision |
| sqlite-vec | Semantic search (phase 2) | One file, no server, shares the audit DB |
| bge-small / MiniLM | Embeddings (phase 2) | ~100MB; larger models add nothing at this corpus size |

### Control and execution

| Technology | Role | Why |
|---|---|---|
| AppleScript / `osascript` | App and window control | Universal on macOS |
| AXUIElement | Structured screen reading | Text, not pixels; milliseconds, not seconds |
| `shortcuts` CLI | Reuse existing Shortcuts | Bridges to automation you already have |
| PyObjC | Python bindings to macOS APIs | Keeps everything in one language |

### Infrastructure

| Technology | Role | Why |
|---|---|---|
| SQLite | Audit log and metrics | Single file, queryable, no server |
| macOS Keychain | Secrets | Never markdown, never in the vault |
| launchd | Process supervision and scheduling | System-native, survives reboot |

**Resident memory: ~5.6GB** with the 8B loaded, **~1GB** at rest if lazy-loading is used. Leaves comfortable headroom on 16GB.

---

## 4. Repository layout

```
mynah/
├── mynah/
│   ├── audio/          wake word, capture, VAD, echo cancellation
│   ├── stt/            whisper wrapper, streaming buffer
│   ├── router/         rules table, local model client, confidence
│   ├── tools/          one module per domain
│   │   ├── apps.py         launch, focus, quit
│   │   ├── windows.py      move, resize, snap
│   │   ├── files.py        move, rename, search
│   │   ├── vault.py        note, search, recall
│   │   ├── clipboard.py    read selection, act on it
│   │   └── systems.py      your own APIs
│   ├── memory/         vault read/write, promotion, compaction
│   ├── tts/            speech out, streaming, mute
│   ├── safety/         confirmation gate, kill switch, budget
│   └── log/            audit writer, SQLite schema
├── rules/
│   └── instant.yaml    the Tier 0 pattern table
├── models/
├── tests/
└── mynah.py
```

The four components an external agent framework would have replaced — tool registry, vault I/O, scheduler, cloud client — total roughly 350 lines. That is the price of full control over the hot path, and it is worth paying.

---

## 5. Vault design

```
vault/
├── me/                  always loaded, under 500 tokens
│   ├── identity.md
│   ├── work.md
│   └── preferences.md
├── facts/               searched on demand
│   ├── projects/
│   └── people/
├── daily/               append-only
│   └── 2026-08-26.md
└── quarantine/          captured externally, never promoted
```

Frontmatter is structured so lookups are dictionary access, not model calls:

```yaml
---
type: identity
name: ...
location: San Jose, CA
role: ...
---
```

### Promotion rules
- Only spoken or typed input can enter `me/` or `facts/`
- Anything captured from a webpage, document, or transcript lands in `quarantine/` with a source tag
- Compaction runs nightly as a single cloud call: extract durable facts, promote them, rewrite the day as a summary
- Secrets never enter the vault at any layer

**The quarantine boundary is the entire defence against injection.** Content cannot instruct the assistant because content never reaches the always-loaded context. Build it in week two, not later.

### Retrieval
Hybrid, in this order:

1. **ripgrep first.** Exact terms, filenames, dates, tags.
2. **Vectors second**, only when grep returns nothing or too much.
3. **Rerank by recency.** In a personal vault, recency is a stronger relevance signal than similarity. Weight it explicitly.

Chunk by heading, not by token count. Your notes already have semantic structure; a 512-token window sliced across two topics does not. This one decision does more for retrieval quality than the choice of embedding model.

Always speak the source: "from your note on the twelfth." Provenance is what makes memory trustworthy rather than merely plausible.

---

## 6. Safety

Build these before the interesting features. Retrofitting them is painful and their absence is what makes an assistant untrustworthy.

**Tool classification.** Every tool is `safe` or `irreversible` in its schema. Safe tools execute. Irreversible tools speak the intended action, wait for spoken confirmation, and time out to a refusal.

Irreversible includes: sending anything, deleting anything, submitting any form, running any shell command, anything involving money.

**Kill switch.** A global hotkey that hard-stops in-flight execution and unloads models. An interrupt, not a graceful shutdown.

**Budget enforcement.** The audit log is queried before every cloud call. Over ceiling, the call does not happen.

**Audit schema.**
```sql
CREATE TABLE turns (
  ts, transcript, frontmost_app, path,
  confidence, tool, args, result,
  tokens_in, tokens_out, cost_usd,
  latency_stt, latency_route, latency_exec,
  confirmed, repeated
);
```

`repeated` marks turns where you had to say the same thing twice. It is your failure signal and the highest-value input to v2.0.

---

## 7. Performance

Target: under 1.5 seconds from end of speech to first spoken word.

| Stage | Budget |
|---|---|
| Wake word | 50ms |
| STT (streaming, mostly done before you stop) | 250ms |
| Route, Tier 0 | 5ms |
| Route, Tier 1 | 300ms |
| Execute | 200ms |
| First TTS audio | 100ms |

Three techniques matter more than everything else combined:

**Streaming transcription.** Transcribe in 500ms windows as speech arrives rather than waiting for silence.

**Sentence-boundary TTS.** Start speaking the first complete sentence while the rest still generates. Turns a 2-second cloud wait into 600ms. Roughly 30 lines of code and the single largest perceived-speed win available.

**Barge-in.** Let speech interrupt playback, via the Voice Processing AudioUnit for echo cancellation.

**Power awareness.** On battery, unload the 8B and route more aggressively to Tier 0 and Tier 2. On mains, keep it resident.

---

## 8. Technologies worth adding later

**Apple Foundation Models framework.** A system-provided ~3B model on macOS 26 with guided generation and a tool protocol that structurally prevents hallucinated tool names. Zero managed RAM, NPU inference, no download. Would take over the routing job and let the 8B load lazily — roughly 5GB freed at rest. Catch: Swift only, needs a small bridge binary, and is absent when Apple Intelligence is off. **Benchmark it in week four.**

**Private Cloud Compute language model.** Same API, larger context, reasoning the on-device model lacks, behind an entitlement. If obtainable for a personal app, a free middle tier between the 8B and Claude that stays inside Apple's privacy boundary. Worth an hour of investigation.

**Semantic response cache.** Embed every question, store question/answer pairs, replay when similarity exceeds ~0.95. Cuts latency and spend to zero on repeats.

**Speaker verification.** A ~50MB speaker-embedding model gating the wake word so only your voice triggers actions.

**LoRA fine-tuned router.** After three months of logs, fine-tune a 0.5B on how you specifically phrase things. Should beat a generic 8B at routing in a tenth of the memory. The piece nobody else can build, because nobody else has your logs.

**Speech-to-speech models.** Collapse STT and TTS into one stage, removing 350ms and two failure points. Currently need 8–16GB for the model alone. Revisit in a year.

---

## 9. Deliberately excluded

| Technology | Why not |
|---|---|
| Vision models for screen understanding | 3–7GB, seconds per step, largest injection surface in the design |
| Browser automation (Playwright, CDP) | Fragile, expensive per task, account-ban risk on sites worth automating |
| Vector database (Qdrant, pgvector, Weaviate) | Operational weight unjustified for a few thousand documents |
| LangChain / LlamaIndex | Abstraction overhead for a system whose point is a thin, fast path |
| External agent runtimes | Built for chat latency, not sub-second voice reflex; adopting one trades the core design goal to save ~350 lines |
| Multi-agent orchestration | Planner/executor/critic adds latency and failure modes with no gain at this scale |
| A GUI | The premise is not looking at the screen |
| Fine-tuning before logs exist | You would be fitting to assumptions about how you talk, which are wrong |

---

## 10. Prior art worth reading, not adopting

| Project | What to take from it |
|---|---|
| Jarvis (jarvis.ceo) | Latency engineering on Apple Silicon; sub-300ms local pipeline |
| Dottie | Breadth of macOS system tools worth exposing |
| SafeClaw | Validates the Tier 0 idea: rule-based, no LLM in the core loop |
| Goose | MCP tool schema shapes |
| General agent runtimes | Markdown memory layout and permission models, solved across large user bases |

Spend an evening running two of these before writing code. Copy the good decisions; write your own implementation.

---

## 11. First file to write

Not the audio pipeline. Write the **audit log schema** and the **tool registry interface** first. Everything else plugs into those two, and getting them right early is what determines whether v2.0 is possible at all.

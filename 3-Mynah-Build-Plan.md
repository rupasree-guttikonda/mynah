# Mynah — Build Plan

Document 3 of 3
Week-by-week to v1.0 and beyond

---

## Ground rules

**Every version must be independently usable.** If you stop at any point, what exists still earns its place. This is the most important rule in the plan, because the failure mode is not bad architecture — it is three months of building and nothing running.

**Definition of done is behavioural, not structural.** "The code compiles" is not done. "I used it five times today without thinking about it" is done.

**Estimates assume 8 to 10 hours per week.** Evenings and weekends.

**Total to v1.0: nine weeks, roughly 81 hours.**

---

## Week 0 — Look before you build

**One evening. Do not skip.**

| Task | Hours |
|---|---|
| Install and use Jarvis (jarvis.ceo) for an hour | 1 |
| Install and use Dottie for an hour | 1 |
| Write one paragraph: what they do well, what's missing, what you'll steal | 1 |

You are not evaluating whether to adopt them. The architecture decision is made: single Python process, no external runtime. You are looking at how they handle latency, which system tools they expose, and where they feel wrong. Two hours here makes your own design better.

---

## v0.1 — Voice loop

**Week 1 · 9 hours · Goal: speak to your Mac and have it do something**

| Day | Task | Hours |
|---|---|---|
| 1 | Project skeleton, SQLite audit schema, tool registry interface | 2 |
| 2 | Audio capture with PyObjC, mic permission, ring buffer | 2 |
| 3 | openWakeWord integration, custom phrase, false-positive tuning | 2 |
| 4 | whisper.cpp `small.en`, transcript on wake | 1.5 |
| 5 | Rules table (10 patterns), tool executor, `say` output, mute flag | 1.5 |

**The ten commands:** open app, quit app, focus window, snap window left/right, volume up/down, what time is it, timer N minutes, note this, mute.

**Definition of done:** you say "Mynah, open Slack" and Slack opens in under one second, five times in a row, with the audit log populated.

**Deliverable:** a working voice launcher. Usable on its own.

**Do not build this week:** any model, any vault, any cloud call.

> Write the audit schema and tool registry interface **before** the audio. Everything plugs into those two.

---

## v0.2 — Memory

**Week 2 · 9 hours · Goal: it remembers things and can find them**

| Day | Task | Hours |
|---|---|---|
| 1 | Vault structure: `me/`, `facts/`, `daily/`, `quarantine/` | 1.5 |
| 2 | Write `me/identity.md`, `work.md`, `preferences.md` by hand | 1 |
| 3 | `vault.append` tool: voice note filed with date and timestamp | 2 |
| 4 | ripgrep search tool, result ranking by recency | 2.5 |
| 5 | Spoken recall with source attribution | 2 |

**The quarantine boundary goes in this week.** Anything captured from a webpage, document, or transcript lands in `quarantine/` with a source tag and never enters always-loaded context. Only spoken or typed input reaches `me/` or `facts/`. This is the entire injection defence and retrofitting it is painful.

**Definition of done:** you capture a note by voice and retrieve it by voice three days later without touching the keyboard.

**Deliverable:** a hands-free notebook you can query. This is the feature you will use most.

---

## v0.3 — Local brain

**Weeks 3–4 · 18 hours · Goal: phrasing stops mattering**

### Week 3

| Day | Task | Hours |
|---|---|---|
| 1 | Ollama, pull Qwen2.5 1.5B Q4_K_M, benchmark tokens/sec and RAM | 2 |
| 2 | Tool schema definition, JSON contract, error handling | 2.5 |
| 3 | Constrained decoding via Ollama tools API or GBNF grammar | 3 |
| 4 | Router: rules first, model on miss, confidence scoring | 2.5 |

### Week 4

| Day | Task | Hours |
|---|---|---|
| 1 | Context injection: frontmost app, identity block, last two turns | 2 |
| 2 | Lazy model loading, unload after idle, memory pressure handling | 2 |
| 3 | **Spike: Apple Foundation Models.** Swift bridge, benchmark against Qwen3 on 50 routing examples | 3 |
| 4 | Decide from the numbers; document the decision | 1 |

**On the spike:** if Apple FM wins, routing moves to it, the 1.5B becomes lazy-loaded for real work only, and you free ~1.1GB at rest. If it loses, you've spent three hours and closed the question permanently. Either outcome is worth it.

**Definition of done:** you phrase a command three different ways and all three work.

**Known limitation to accept:** a 1.5B/3B is reliable on single tool calls, shaky on multi-step chains. Design around single-step commands; let chains escalate.

---

## v0.4 — Escalation and guardrails

**Week 5 · 9 hours · Goal: no knowledge ceiling, no runaway spend**

| Day | Task | Hours |
|---|---|---|
| 1 | OpenAI API client, gpt-4o-mini default, schema definitions | 2 |
| 2 | Confidence-based routing, gpt-4o-mini escalation on low confidence | 2 |
| 3 | Hard token cap per request (8,000), enforced before the call | 1.5 |
| 4 | Daily spend ceiling ($1) queried from the audit log, spoken refusal at limit | 2 |
| 5 | Cost and latency columns wired into every log row | 1.5 |

**Definition of done:** you ask a question the local model can't answer, get a good spoken answer, and see the cost in your log. Then set the ceiling to $0.01 and confirm it refuses.

---

## v0.5 — Capture

**Weeks 6–7 · 18 hours · Goal: it stops being a tool and becomes a habit**

### Week 6 — Meetings and compaction

| Day | Task | Hours |
|---|---|---|
| 1 | Continuous local transcription mode, start/stop by voice | 3 |
| 2 | Basic speaker segmentation (you vs. others) | 2 |
| 3 | End-of-meeting summarization: decisions and action items to vault | 2.5 |
| 4 | Nightly compaction via launchd: promote durable facts, rewrite the day | 2.5 |

### Week 7 — Clipboard as context

| Day | Task | Hours |
|---|---|---|
| 1 | Clipboard read tool, selection capture | 1.5 |
| 2 | Clipboard actions: explain, summarize, rewrite, translate | 3 |
| 3 | Route clipboard work to local 1.5B/3B by default, cloud on length or complexity | 2 |
| 4 | Learning tools: quiz me from my notes, summarize what I learned this month | 2.5 |

**The clipboard is what replaces screen control.** Select anything in any app, speak, act on it. No perception problem, no token cost of a full page, no injection surface, works in apps with no accessibility tree. Ninety percent of what screen control promised at five percent of the complexity.

**Definition of done:** a week of meetings produces usable notes you didn't type, and you use clipboard actions without thinking about it.

---

## v1.0 — Daily driver

**Weeks 8–9 · 18 hours · This is the release**

### Week 8 — Safety and control

| Day | Task | Hours |
|---|---|---|
| 1 | Tool classification: `safe` vs `irreversible` in every schema | 1.5 |
| 2 | Confirmation gate: speak intent, await spoken yes, timeout to refusal | 3 |
| 3 | Global kill switch hotkey: interrupt execution, unload models | 2 |
| 4 | Menu bar app: status, mute toggle, today's spend, kill switch | 3 |

### Week 9 — Performance and polish

| Day | Task | Hours |
|---|---|---|
| 1 | Streaming transcription in 500ms windows | 2.5 |
| 2 | Sentence-boundary streaming TTS | 2 |
| 3 | Barge-in with Voice Processing AudioUnit echo cancellation | 3 |
| 4 | Power-aware residency: unload 8B on battery | 1 |
| 5 | Focus modes, launchd supervision, crash recovery | 2 |

**Irreversible includes:** sending anything, deleting anything, submitting any form, running any shell command, anything involving money.

**Definition of done:** it runs for seven consecutive days without being restarted, and you notice when it's not running.

**Everything above this line is the product.**

---

## Interlude — Use it for a month

**Weeks 10–13 · Build nothing**

Run it daily. Let the logs accumulate. Resist adding features.

At the end, query the audit log:

- What percentage of requests hit each tier?
- What was actual monthly spend?
- p50 and p95 latency by tier?
- Which requests are you repeating most?
- Where did `repeated = true` cluster?

**These numbers decide v1.5 and v2.0.** They will disagree with what you currently think, which is the point of waiting.

**This is also the month to write it up.** One technical post on the routing design and its measured cost impact. The numbers exist now; they didn't before.

---

## v1.5 — Work integrations

**Weeks 14–15 · 18 hours · Goal: it touches your real work**

| Task | Hours |
|---|---|
| MCP client, connect to existing servers | 3 |
| Airflow API tool: DAG status, failures, last run | 3 |
| Snowflake tool: read-only queries, spoken results, row-count guard | 4 |
| Calendar and mail: read-only, senders and subjects only | 3 |
| Job APIs: search by voice, save interesting roles to vault | 3 |
| Writes behind the confirmation gate | 2 |

**Design rule:** read-only first. Every write path goes through confirmation, no exceptions, no "just this one is safe."

**Definition of done:** you stop opening a browser tab to check whether the nightly load finished.

---

## v2.0 — Learning

**Weeks 16–18 · 24 hours · Requires the month of logs to exist**

| Task | Hours |
|---|---|
| Promotion detector: find requests hitting the model path repeatedly with stable output | 4 |
| Auto-generate rules into the Tier 0 table, with review before activation | 4 |
| Eval harness: 200 labelled routing examples from real logs, scored | 5 |
| Macro recording: capture a manual sequence, name it, register as a tool | 5 |
| Semantic response cache with embedding similarity | 3 |
| Optional: LoRA fine-tune a 0.5B router on accumulated logs | 3 |

**The eval harness is the most career-relevant thing in this plan.** A labelled set, a score, and a graph of that score improving is what separates engineering from prompting. Build it even if you skip everything else in v2.0.

**Definition of done:** the Tier 0 table grew by at least ten rules you did not write by hand.

---

## v3.0 — Assisted forms

**Optional · Reconsider only if v2.0 is stable**

One-shot form filling from vault data via the accessibility tree. Field labels mapped by a lookup table you maintain, model only as fallback.

**No loops. No autonomy. No submission.** Fill, speak "12 fields filled, review and submit," stop.

**Time: 8 hours.** Reconsider whether the need is still real. It may not be.

---

## Never build

| Item | Reason |
|---|---|
| Screenshot-based screen understanding | 3–7GB, seconds per step, largest injection surface |
| Autonomous browser agents | Fragile, expensive, account-ban risk |
| Multi-agent orchestration | Latency and failure modes, no gain at this scale |
| A full GUI | The premise is not looking at the screen |
| Fine-tuning before logs exist | Fitting to assumptions about how you talk |

---

## Summary

| Version | Weeks | Cumulative hours | What you get |
|---|---|---|---|
| 0.1 | 1 | 9 | Voice launcher |
| 0.2 | 2 | 18 | Voice notebook with recall |
| 0.3 | 3–4 | 36 | Understands natural phrasing |
| 0.4 | 5 | 45 | Unlimited knowledge, capped spend |
| 0.5 | 6–7 | 63 | Meeting capture, clipboard actions |
| **1.0** | **8–9** | **81** | **Daily driver — the release** |
| — | 10–13 | 81 | Use it. Measure. Write it up. |
| 1.5 | 14–15 | 99 | Connected to real work |
| 2.0 | 16–18 | 123 | Improves itself |

---

## The one thing that determines success

Not the architecture. Whether v0.1 exists in seven days.

Everything here is designed so that stopping early still leaves you with something you use. The plan is only worth following if week one actually happens.

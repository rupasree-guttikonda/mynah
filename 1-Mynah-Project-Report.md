# Mynah

**A local-first voice assistant with persistent memory, for macOS**

Document 1 of 3 — Project Report
August 2026 · Vijay

---

## The name

A mynah is a bird renowned for its incredible ability to mimic human speech, learn sounds, and interact dynamically.

That is what this system does. Every day you use it, it stores a little more about how you work, what you decided, and how you phrase things. The assistant that exists in month six is one you built by using it, not one you programmed.

---

## 1. The problem

Everything on a computer sits behind a screen and a keyboard. That is fine for creative work and poor for the fifty small mechanical acts that fill a day: opening the same four apps, remembering what you decided last Tuesday, retyping the same information into the same kind of form, checking whether a job finished, writing down a thought before it evaporates.

Existing assistants fail in one of two ways.

**Siri and its equivalents** are fast and private but cannot reason, cannot remember anything beyond the current sentence, and cannot be extended.

**Cloud assistants** can reason but know nothing about you, cost money per interaction, require the network, and send everything you say to a third party.

Neither remembers. That is the actual gap. An assistant that forgets you between sessions is a search engine with a voice.

---

## 2. What Mynah is

A background process on a Mac that listens for a wake word, understands what you asked, does it, and speaks back. It keeps a memory of you as plain markdown files you own and can read.

**Local first.** Speech recognition, intent parsing, note capture, retrieval, and most reasoning happen on the machine. Nothing leaves unless a request genuinely needs a frontier model.

**Persistent.** Everything worth keeping is written to a markdown vault. The assistant reads that vault as context, so it knows your role, your projects, your preferences, and what you told it last month.

**Bounded.** It does not attempt to control arbitrary applications or browse the web autonomously. It does a defined set of things reliably. That constraint is a design decision, not a limit of ambition.

**Self-contained.** One Python process. One language. No IPC, no second runtime, no external agent framework. Every line is yours.

---

## 3. Who it is for

**Primary user:** one person. This is a tool built for its author. Anything that makes it a product for other people is out of scope until it is proven for one.

**Profile:** a technical worker moving between a terminal, a browser, a notes app, and a set of internal systems. Learns continuously. Generates a lot of small facts and decisions that get lost.

**Later, potentially:** developers who want a local assistant they can extend, and users for whom voice control is not a convenience but the interface.

---

## 4. What it does

### Capture
- Voice notes filed into the vault with date, topic, and links
- Meeting and call transcription, summarised into decisions and action items
- Automatic end-of-day compaction: the raw log becomes a short summary, durable facts promoted into permanent files

### Recall
- Question answering against your own vault
- Retrieval of stable personal facts for reuse
- Cross-referencing across notes

### Control
- Application and window management
- File operations
- Focus modes: one command reconfigures the machine for a kind of work
- Queries against your own systems (schedulers, warehouses, calendars, mail) through their APIs

### Think
- Explain, summarise, rewrite, or translate whatever is on your clipboard
- Answer questions, locally where possible and via a frontier model where not
- Draft messages from a spoken description

### Speak
- Spoken replies, mutable at any time
- Text-only mode for when you are in company

---

## 5. Why this and not something else

| Approach | What it gets right | Where it fails |
|---|---|---|
| Siri / built-in assistants | Fast, private, zero setup | No memory, no reasoning, not extensible |
| Cloud assistant apps | Strong reasoning | No memory of you, per-use cost, requires network |
| Screen-control agents | Impressive scope | Slow, unreliable, expensive per task, large security surface |
| General agent runtimes | Mature tooling, community | Built for chat-latency, not sub-second voice reflex |
| Dictation tools | Excellent at one job | Only transcribe; no understanding or action |
| **Mynah** | Memory, local reasoning, near-zero cost, bounded reliability | Deliberately cannot control arbitrary GUI apps |

The differentiator is not capability. It is that **the memory compounds and the marginal cost is zero**, which together mean the tool gets better and cheaper the more it is used. Every other option is static and metered.

---

## 6. Constraints

### Hard
- **Memory.** 16GB total, with macOS and normal work taking 6 to 8GB. Resident footprint stays under 7GB and degrades gracefully under pressure.
- **Latency.** Under 1.5 seconds from end of speech to first spoken word on local paths. Beyond that the interaction feels broken.
- **Permissions.** Microphone, Accessibility, Automation, and Full Disk Access each granted manually. Fine for personal use; a real obstacle to distribution.
- **Battery.** Always-on listening costs roughly 3 to 5% additional drain. Model residency must be power-aware.

### Deliberate
- **No screenshot-based screen understanding.** Costs memory the machine cannot spare, is unreliable, and creates the largest security surface in the system.
- **No autonomous multi-step web browsing.** Expensive, fragile, and against the terms of most sites worth automating.
- **No irreversible action without confirmation.** Send, delete, submit, purchase, and pay always stop and ask.
- **No secrets in the vault.** Identifiers, credentials, and financial details live in macOS Keychain, never in markdown.
- **No external agent runtime.** The premise is a fast path fully under your control. A general-purpose agent framework is built for chat latency, not voice reflex, and adopting one would trade the core design goal for roughly 350 lines of saved code.

### Accepted limitations
- Applications with no scripting interface and no accessibility tree cannot be controlled. Roughly 10% of software, not worth solving.
- The local model will be wrong about niche facts. Anything needing current information or deep reasoning escalates.
- An 1.5B/3B model is reliable on single tool calls and shaky on multi-step chains. Design around single-step commands; let chains escalate.

---

## 7. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Prompt injection from captured content | High | Captured text quarantined, tagged by source, never promoted into always-loaded context. Only spoken or typed input becomes permanent memory. |
| Runaway API spend | Medium | Hard token cap per request, daily spend ceiling enforced in code, no unattended loops. |
| Vault as a plaintext liability | Medium | No secrets in vault. Encrypted disk. Keychain for anything sensitive. |
| Accidental irreversible action | Medium | Confirmation gate on all destructive tools, global kill switch, full audit log. |
| Sole maintainer, no community | Medium | Accepted cost of full control. Keep the codebase small enough that it stays understandable. |
| **Abandoned before useful** | **High** | Every version independently usable. Ship v0.1 in a week. |

The last one is the real risk. Every technical problem here has a known solution. The failure mode for a project this open-ended is three months of architecture and nothing running.

---

## 8. Cost

### Build

| Item | Cost |
|---|---|
| All software and model weights | $0 |
| Hardware | $0 (existing machine) |
| Apple Developer account | $0 personal use; $99/yr only to distribute |
| API spend during development | $10 to $20 |
| **Total cash** | **under $20** |

Time is the real cost: roughly 80 hours to v1.0, spread over nine weeks of evenings.

### Running

Local requests cost nothing. With a 1.5B/3B model handling most reasoning, expect roughly 95% of requests to stay on-device.

Rates as of August 2026: gpt-4o-mini at $0.15/$0.60 per million input/output tokens. Prompt caching cuts repeated input cost by 90%.

| Scenario | Cloud calls/day | Monthly |
|---|---|---|
| Light | 3 | under $0.50 |
| Typical | 8 | ~$1.00 |
| Heavy | 20 | ~$2.50 |
| Nightly compaction | 1 | ~$0.30 |

**Expected total: $1 to $3 per month.** A hard daily ceiling of $1 makes overruns structurally impossible.

---

## 9. Versions at a glance

Full detail in Document 3.

| Version | Weeks | What you get |
|---|---|---|
| 0.1 | 1 | Voice launcher — ten commands, no model |
| 0.2 | 2 | Voice notebook with recall |
| 0.3 | 3–4 | Understands natural phrasing |
| 0.4 | 5 | Unlimited knowledge, capped spend |
| 0.5 | 6–7 | Meeting capture, clipboard actions |
| **1.0** | **8–9** | **Daily driver — the release** |
| — | 10–13 | Use it. Measure. Write it up. |
| 1.5 | 14–15 | Connected to real work |
| 2.0 | 16–18 | Improves itself |

Each version must be independently usable. If development stops at any point, what exists still earns its place.

---

## 10. Success criteria

Three months after v1.0:

- Running every day without being restarted or babysat
- More than 90% of requests served locally
- Monthly spend under $5
- The vault contains information genuinely useful for recall
- At least one daily task permanently replaced

It fails if it becomes something demonstrated rather than used.

---

## 11. Career value — an honest assessment

### By default, this does not help you get hired

A voice assistant reads as a hobbyist AI project. It does not signal "data engineer," and for Senior Data Engineer roles it may suggest attention spent on personal tooling rather than platform work.

It also does not close an experience gap. No three-month side project does. Targeted applications, referrals, and interview performance do.

### There is a version that helps

The value is not the assistant. It is four subsystems inside it:

| Subsystem | What it demonstrates | Maps to |
|---|---|---|
| Three-tier router with cost ceiling | Cost optimization under constraint, with measured spend reduction | AI platform / infra |
| Vault ingestion, promotion, compaction | A real ETL pipeline with dedup, promotion rules, scheduled compaction | Core data engineering |
| Hybrid grep + vector retrieval | Retrieval design with honest tradeoff reasoning | AI engineering, RAG |
| Audit log driving self-improvement | A data flywheel: instrumentation feeding model improvement | The most senior-sounding piece |

Framing decides everything:

- **Weak:** "I built a Siri replacement for my Mac."
- **Strong:** "I built a local-first agent runtime with a three-tier routing layer that keeps 95% of requests on-device, cutting LLM spend to under $3/month, backed by a markdown ingestion pipeline and an evaluation harness built from usage logs."

Same project. The second is a platform engineering story.

### What makes it count

1. **Measure everything and publish the numbers.** Requests by tier, cost per request, p50 and p95 latency, routing accuracy. Real metrics beat a demo video.
2. **Build an eval harness.** 200 labelled routing examples, a score, a graph of that score improving. This separates people who use models from people who engineer with them, and most candidates cannot show it.
3. **Write it up.** One clear technical post on the routing decision and its measured cost impact. Linkable, survives a recruiter skim, demonstrates communication.
4. **Finish it.** A shipped v1.0 used daily beats an ambitious v3.0 that never ran.

### Opportunity cost, stated plainly

This is roughly 80 hours to v1.0. Those hours compete directly with applications, outreach, and interview preparation.

A finished, measured, written-up project is worth more than several started ones — to a hiring manager, and to you, because a finished project is evidence and an unfinished one is only intention.

**Build this because you will use it every day and it will make your work easier.** That is sufficient reason. Treat career benefit as a secondary effect that materialises only if you finish it, measure it, and write it up.

If the goal is specifically hiring, the higher-return version is smaller: build the routing layer and the eval harness, two weeks not three months, publish the numbers, and put the remaining hours into applications.

---

## 12. What this is not

Not a product. Not a startup. Not a replacement for Siri for anyone but its author. Not an attempt to control every application. Not a general-purpose autonomous agent.

It is a personal tool, built to a defined scope, that gets better through use.

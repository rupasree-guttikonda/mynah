# Mynah Project Rules & Coding Guidelines

This document provides instructions for any AI assistant or agent working within the Mynah project workspace. These rules are automatically loaded by the Antigravity Coder.

---

## 🚫 Hard Architectural Rules

* **Single Python Process:** All core audio capture, transcription, routing, tool execution, and voice output MUST run in the same single Python process. 
* **No External Agent Frameworks:** Do NOT introduce LangChain, LlamaIndex, AutoGPT, or other agent orchestrators. The path from microphone to action should remain a direct chain of Python function calls.
* **No Web GUI:** Mynah is a voice/keyboard-driven background service with a simple macOS Menu Bar indicator. Do not write web/GUI app frameworks.
* **Database First:** The SQLite audit database (`turns` table) is the source of truth for metrics, costs, and feedback logs. Design all tool executions to log to SQLite.
* **Quarantine Boundary:** Any document, web page content, or external transcript must reside in the `quarantine/` folder in the Vault, marked with source headers. They MUST never be injected directly into the active prompt context to prevent prompt injection.

---

## 🐍 Python Coding Style & Technology Stack

* **macOS Integration:** Use PyObjC for native API bindings (Audio recording, menu bar UI, accessibility AXUIElement APIs).
* **Process Supervision:** Use standard plist setups for macOS launchd.
* **Asynchronous Execution:** Use standard asyncio or threading loops for non-blocking speech recognition and audio ring buffers.
* **Model Constraints:** 
  * Local LLM routing runs on Qwen 8B (via Ollama/MLX) utilizing structured output (JSON mode or GBNF grammar templates).
  * Cloud LLM runs on Anthropic Claude (Haiku for default, Sonnet for low confidence) with system prompt caching enabled.

---

## 🔒 Safety and Guardrails

* **Tool Classification:** Every tool in `mynah/tools/` must declare its classification metadata: `safe` or `irreversible`.
* **Confirmation Gate:** Any tool marked as `irreversible` (e.g. deleting files, running shell commands, sending messages) must halt execution, play/speak a confirmation request, and await a spoken "yes". Timeout to refusal in 10 seconds.
* **Budget Limits:** Every cloud call must query the SQLite audit log to verify that the daily budget has not exceeded the $1.00 threshold. If exceeded, immediately return a spoken refusal.


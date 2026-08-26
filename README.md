# Mynah

Mynah is a local-first voice assistant with persistent memory for macOS. 

This project is built collaboratively by a two-developer team, using Google Antigravity to its full potential as an active AI pair programmer.

## 🚀 Getting Started

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd mynah
   ```

2. **Set Up the Vault:**
   Mynah uses a local Markdown directory called the `vault/` for its long-term memory. Since the vault is ignored in Git (via `.gitignore`), you must initialize your own private vault structure on your laptop:
   ```bash
   mkdir -p vault/{me,facts,daily,quarantine}
   touch vault/me/identity.md vault/me/work.md vault/me/preferences.md
   ```
   *Tip: You can open the `vault/` folder as a vault in [Obsidian](https://obsidian.md) to inspect and manage your assistant's memory.*

3. **Explore Documentation:**
   - Detailed specifications and design can be found in:
     - [`1-Mynah-Project-Report.md`](1-Mynah-Project-Report.md)
     - [`2-Mynah-Technical-Design.md`](2-Mynah-Technical-Design.md)
     - [`3-Mynah-Build-Plan.md`](3-Mynah-Build-Plan.md)
     - [`4-Collaborative-Build-Plan.md`](4-Collaborative-Build-Plan.md)

---

## 👥 Team Roles & Git Workflow

- **Dev A (Systems & Audio):** Responsible for audio capture, wake word detection, STT/TTS, and SQLite metrics.
- **Dev B (Logic & Brain):** Responsible for app shell, tool registry, routing tier, local/cloud LLM clients, and memory vault.
- **Branching Model:** 
  - Do not commit directly to `main`.
  - Create feature branches (e.g. `dev-a/audio-pipeline`, `dev-b/vault-core`).
  - Keep your branches updated with `main`.
  - Merge branches to `main` during the weekend integration sync.

---

## 🤖 Antigravity Customizations

This workspace is customized to make Antigravity an expert on the Mynah codebase:
- **Rules (`GEMINI.md`):** Automatically loaded by Antigravity to enforce architectural boundaries, coding styles, and safety.
- **Skills (`.agents/skills/mynah-builder`):** Contains instructions on building, running tests, and checking metrics.

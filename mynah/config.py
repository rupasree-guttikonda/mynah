# mynah/config.py
"""
Configuration management for Mynah, including dynamic RAM detection
and tiered default local model selection.
"""

import os

# Base directory for the personal vault notes
VAULT_DIR = os.getenv("MYNAH_VAULT_DIR", "vault")

# Cloud model configurations
OPENAI_MODEL = "gpt-4o-mini"
DAILY_BUDGET_LIMIT = 1.00  # USD

def get_system_ram_gb() -> float:
    """Returns the total physical system RAM in gigabytes."""
    try:
        # Standard POSIX sysconf query
        page_size = os.sysconf('SC_PAGE_SIZE')
        phys_pages = os.sysconf('SC_PHYS_PAGES')
        total_memory_bytes = page_size * phys_pages
        return total_memory_bytes / (1024 ** 3)
    except Exception:
        # Fallback to standard 16GB if lookup fails
        return 16.0

def get_default_local_model() -> str:
    """
    Returns the single default local model configured for the project.
    - Default local model: Qwen 3.5 4B (qwen3.5:4b)
    """
    return "qwen3.5:4b"

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
    Returns default local model based on system RAM or MYNAH_LOCAL_MODEL env var.
    - <= 8.5 GB RAM: qwen3:1.7b
    - > 8.5 GB RAM: qwen3.5:4b
    """
    env_model = os.getenv("MYNAH_LOCAL_MODEL")
    if env_model:
        return env_model

    ram_gb = get_system_ram_gb()
    if ram_gb <= 8.5:
        return "qwen3:1.7b"
    else:
        return "qwen3.5:4b"

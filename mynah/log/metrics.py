# mynah/log/metrics.py
"""
Metrics & safety ceiling enforcement for Mynah.
Tracks token counts with tiktoken and validates daily budget spend limit ($1.00 USD).
"""

import sqlite3
import datetime
from typing import Tuple

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


def count_tokens(text: str, model_name: str = "gpt-4o-mini") -> int:
    """
    Counts tokens for a string using tiktoken.
    Falls back to word count estimation if tiktoken is unavailable.
    """
    if not text:
        return 0

    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.encoding_for_model(model_name)
            return len(encoding.encode(text))
        except Exception:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception:
                pass

    # Estimation fallback: ~4 characters per token
    return max(1, len(text) // 4)


def check_daily_budget(db_path: str = "audit.db", max_usd: float = 1.00) -> Tuple[bool, float]:
    """
    Queries SQLite audit turns table to sum today's cloud API cost in USD.
    Returns (within_budget: bool, current_total_usd: float).
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query total USD cost logged today
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT SUM(cost_usd) FROM turns
            WHERE date(ts) = date(?)
            """,
            (today_str,),
        )
        row = cursor.fetchone()
        current_cost = row[0] if row and row[0] is not None else 0.0
        conn.close()

        within_budget = current_cost < max_usd
        return within_budget, current_cost
    except Exception:
        # If DB query fails or table doesn't exist yet, permit execution
        return True, 0.0

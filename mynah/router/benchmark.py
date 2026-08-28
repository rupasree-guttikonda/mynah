# mynah/router/benchmark.py
"""
Performance benchmarker for local LLMs running via Ollama.
Measures token generation throughput (tokens/sec) and system RAM usage.
"""

import time
import requests
from mynah.config import get_default_local_model, get_system_ram_gb


def benchmark_ollama(model_name: str = None, prompt: str = "Explain voice assistants in 2 sentences.") -> dict:
    """
    Benchmarks token generation speed (tokens/sec) for Ollama local model.
    """
    if model_name is None:
        model_name = get_default_local_model()

    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30.0,
        )
        latency = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            eval_count = data.get("eval_count", 0)
            eval_duration_ns = data.get("eval_duration", 1)
            tokens_per_sec = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0
            return {
                "success": True,
                "model": model_name,
                "latency_sec": latency,
                "tokens_generated": eval_count,
                "tokens_per_sec": tokens_per_sec,
                "system_ram_gb": get_system_ram_gb(),
            }
        return {
            "success": False,
            "error": f"Ollama HTTP {response.status_code}",
            "latency_sec": latency,
            "system_ram_gb": get_system_ram_gb(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "latency_sec": time.time() - start_time,
            "system_ram_gb": get_system_ram_gb(),
        }

from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(provider, model, usage)
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, provider: str, model: str, usage: Dict[str, int]) -> float:
        """
        Rough, configurable cost estimation in USD.
        Local models default to zero marginal cost for this lab.
        """
        pricing_per_1k = {
            ("openai", "gpt-4o"): 0.01,
            ("openai", "gpt-4o-mini"): 0.001,
            ("google", "gemini-1.5-flash"): 0.001,
            ("local", "default"): 0.0,
        }

        key = (provider.lower(), model)
        unit_price = pricing_per_1k.get(key)

        if unit_price is None:
            unit_price = pricing_per_1k.get((provider.lower(), "default"), 0.002)

        return (usage.get("total_tokens", 0) / 1000.0) * unit_price

    def _percentile(self, values: List[float], pct: float) -> float:
        """Computes percentile with linear interpolation (pct in [0, 100])."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        if len(sorted_values) == 1:
            return float(sorted_values[0])

        rank = (pct / 100.0) * (len(sorted_values) - 1)
        lower = int(rank)
        upper = min(lower + 1, len(sorted_values) - 1)
        weight = rank - lower

        return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * weight

    def summarize(self) -> Dict[str, Any]:
        """
        Aggregate metrics for a run/test suite:
        - average_latency_p50_ms (median)
        - max_latency_p99_ms
        - average_tokens_per_task
        - total_cost_test_suite_usd
        """
        if not self.session_metrics:
            return {
                "total_tasks": 0,
                "average_latency_p50_ms": 0.0,
                "max_latency_p99_ms": 0.0,
                "average_tokens_per_task": 0.0,
                "total_cost_test_suite_usd": 0.0,
            }

        latencies = [float(m.get("latency_ms", 0)) for m in self.session_metrics]
        total_tokens = sum(int(m.get("total_tokens", 0)) for m in self.session_metrics)
        total_cost = sum(float(m.get("cost_estimate", 0.0)) for m in self.session_metrics)
        total_tasks = len(self.session_metrics)

        summary = {
            "total_tasks": total_tasks,
            "average_latency_p50_ms": round(self._percentile(latencies, 50), 2),
            "max_latency_p99_ms": round(self._percentile(latencies, 99), 2),
            "average_tokens_per_task": round(total_tokens / total_tasks, 2),
            "total_cost_test_suite_usd": round(total_cost, 6),
        }

        logger.log_event("LLM_METRICS_SUMMARY", summary)
        return summary

    def reset(self) -> None:
        """Clears in-memory metrics for a fresh run."""
        self.session_metrics.clear()

# Global tracker instance
tracker = PerformanceTracker()

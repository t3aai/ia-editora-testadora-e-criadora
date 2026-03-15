"""
Cost tracking for LLM API usage.
"""

import logging
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass
class CostInfo:
    input_cost: float
    output_cost: float
    total_cost: float


PRICING = {
    "anthropic": {
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    },
    "openai": {
        "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
        "gpt-4-turbo-2024-04-09": {"input": 10.00, "output": 30.00},
    },
    "gemini": {
        "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
    }
}


class CostTracker:
    def __init__(self):
        self.costs: list[dict] = []

    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> CostInfo:
        provider_pricing = PRICING.get(provider, {})
        model_pricing = provider_pricing.get(model)
        if not model_pricing:
            model_pricing = {"input": 5.00, "output": 15.00}

        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        return CostInfo(
            input_cost=round(input_cost, 6),
            output_cost=round(output_cost, 6),
            total_cost=round(input_cost + output_cost, 6)
        )

    def extract_token_usage(self, response_metadata: dict) -> Optional[TokenUsage]:
        usage = response_metadata.get("usage") or response_metadata.get("token_usage")
        if not usage:
            return None
        input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0
        total_tokens = usage.get("total_tokens") or (input_tokens + output_tokens)
        return TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens)

    def track_usage(self, provider: str, model: str, agent_type: str, response_metadata: dict,
                    job_id: Optional[str] = None, user_id: Optional[str] = None,
                    project_id: Optional[str] = None) -> Optional[dict]:
        usage = self.extract_token_usage(response_metadata)
        if not usage:
            return None

        cost = self.calculate_cost(provider, model, usage.input_tokens, usage.output_tokens)
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider, "model": model, "agent_type": agent_type,
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "input_cost": cost.input_cost, "output_cost": cost.output_cost,
            "total_cost": cost.total_cost,
            "job_id": job_id, "user_id": user_id, "project_id": project_id,
        }
        self.costs.append(record)
        logger.info(f"Tracked: {provider}/{model} - Tokens: {usage.total_tokens}, Cost: ${cost.total_cost:.6f}")
        return record

    def get_total_cost(self) -> float:
        return sum(r["total_cost"] for r in self.costs)


cost_tracker = CostTracker()

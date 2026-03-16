"""
Base agent class with LLM integration.
"""

import logging
from typing import Optional
from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage, HumanMessage

from app.llm.provider_manager import llm_manager, ProviderType
from app.llm.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, agent_type: str, preferred_provider: Optional[ProviderType] = None):
        self.agent_type = agent_type
        self.preferred_provider = preferred_provider
        self.conversation_history: list = []
        logger.info(f"Initialized {agent_type} agent")

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def invoke(self, user_message: str, context: Optional[dict] = None,
               job_id: Optional[str] = None, user_id: Optional[str] = None,
               project_id: Optional[str] = None) -> tuple[str, dict]:
        messages = [SystemMessage(content=self.get_system_prompt())]
        messages.extend(self.conversation_history)
        messages.append(HumanMessage(content=user_message))

        try:
            response, provider, metadata = llm_manager.invoke_with_fallback(
                messages=messages, preferred_provider=self.preferred_provider,
                json_mode=True
            )
            if metadata.get("usage"):
                cost_tracker.track_usage(
                    provider=provider, model=metadata.get("model", "unknown"),
                    agent_type=self.agent_type, response_metadata=metadata,
                    job_id=job_id, user_id=user_id, project_id=project_id
                )
            self.conversation_history.append(HumanMessage(content=user_message))
            self.conversation_history.append(response)
            return response.content, {
                "provider": provider, "model": metadata.get("model"),
                "agent_type": self.agent_type, "usage": metadata.get("usage"), "success": True
            }
        except Exception as e:
            logger.error(f"Agent invocation failed: {str(e)}")
            raise

    def reset_conversation(self):
        self.conversation_history = []

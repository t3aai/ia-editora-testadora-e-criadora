"""
Analyzer Agent - Identifies issues and violations in documents.
"""

import json
import logging
import os
from typing import Optional

from app.agents.base_agent import BaseAgent, ProviderType
from app.utils.json_utils import parse_llm_json

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class AnalyzerAgent(BaseAgent):
    def __init__(self, preferred_provider: Optional[ProviderType] = None):
        super().__init__(agent_type="analyzer", preferred_provider=preferred_provider)
        self._load_rules()

    def _load_rules(self):
        try:
            with open(os.path.join(BASE_DIR, "regras", "REGRAS_PROMPT_CLIENTE.md"), 'r', encoding='utf-8') as f:
                self.rules_prompt = f.read()
            with open(os.path.join(BASE_DIR, "regras", "REGRAS_BASE_DE_DADOS.md"), 'r', encoding='utf-8') as f:
                self.rules_database = f.read()
            logger.info("Successfully loaded T3A rules")
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            self.rules_prompt = "[Rules not available]"
            self.rules_database = "[Rules not available]"

    def get_system_prompt(self) -> str:
        prompt_path = os.path.join(BASE_DIR, "app", "prompts", "analyzer_prompt.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return template.format(rules_prompt=self.rules_prompt, rules_database=self.rules_database)

    def analyze(self, document_content: str, document_type: str,
                job_id: Optional[str] = None, user_id: Optional[str] = None,
                project_id: Optional[str] = None) -> dict:
        user_message = f"""Analise o seguinte documento do tipo "{document_type}":

```markdown
{document_content}
```

Retorne sua análise completa em formato JSON conforme especificado."""

        response, metadata = self.invoke(
            user_message=user_message, job_id=job_id, user_id=user_id, project_id=project_id
        )

        try:
            analysis = parse_llm_json(response)
            analysis["_metadata"] = metadata
            return analysis
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {"error": "Failed to parse analysis", "raw_response": response, "_metadata": metadata}

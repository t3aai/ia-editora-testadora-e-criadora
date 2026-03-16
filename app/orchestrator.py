"""
Orchestrator - Coordinates the multi-agent editing workflow.
Supports both full document editing and granular change generation.
"""

import json
import logging
import os
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.editor_agent import EditorAgent
from app.agents.validator_agent import ValidatorAgent
from app.document_processor import document_processor
from app.utils.markdown_utils import markdown_processor
from app.llm.provider_manager import llm_manager
from app.llm.cost_tracker import cost_tracker
from app.utils.json_utils import parse_llm_json
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@dataclass
class WorkflowProgress:
    step: str
    progress: int
    message: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class Orchestrator:
    def __init__(self, progress_callback: Optional[Callable[[WorkflowProgress], None]] = None):
        self.progress_callback = progress_callback
        logger.info("Orchestrator initialized")

    def _report_progress(self, step: str, progress: int, message: str):
        if self.progress_callback:
            self.progress_callback(WorkflowProgress(step=step, progress=progress, message=message))
        logger.info(f"[{progress}%] {step}: {message}")

    def _load_rules(self) -> tuple[str, str, str]:
        try:
            with open(os.path.join(BASE_DIR, "regras", "REGRAS_PROMPT_CLIENTE.md"), 'r', encoding='utf-8') as f:
                rules_prompt = f.read()
            with open(os.path.join(BASE_DIR, "regras", "REGRAS_BASE_DE_DADOS.md"), 'r', encoding='utf-8') as f:
                rules_database = f.read()
            knowledge_base = ""
            kb_path = os.path.join(BASE_DIR, "regras", "EDITOR_KNOWLEDGE_BASE.md")
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    knowledge_base = f.read()
                logger.info(f"Loaded EDITOR_KNOWLEDGE_BASE.md ({len(knowledge_base)} chars)")
            return rules_prompt, rules_database, knowledge_base
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return "[Rules not available]", "[Rules not available]", ""

    def generate_edit_changes(
        self,
        edit_request: str,
        prompt_content: str = "",
        base_content: str = "",
        general_prompt_content: str = "",
        document_types: list[str] = None,
        job_id: Optional[str] = None,
    ) -> dict:
        """
        Generate granular edit changes based on user request.
        Returns list of individual changes with before/after/reason.
        """
        if document_types is None:
            document_types = ["prompt", "base_de_dados", "prompt_geral"]

        self._report_progress("initialization", 0, "Starting edit analysis")

        # Load rules and prompt template
        rules_prompt, rules_database, knowledge_base = self._load_rules()

        prompt_path = os.path.join(BASE_DIR, "app", "prompts", "edit_changes_prompt.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_template = f.read()

        # Use replace instead of format to avoid issues with JSON curly braces
        system_prompt = system_template
        system_prompt = system_prompt.replace("{rules_prompt}", rules_prompt)
        system_prompt = system_prompt.replace("{rules_database}", rules_database)
        system_prompt = system_prompt.replace("{knowledge_base}", knowledge_base)

        # Build user message with documents
        self._report_progress("analysis", 20, "Preparing documents for analysis")

        docs_text = ""
        if "prompt" in document_types and prompt_content.strip():
            docs_text += f"\n\n## PROMPT DO CLIENTE (field: prompt)\n```markdown\n{prompt_content}\n```"
        if "base_de_dados" in document_types and base_content.strip():
            docs_text += f"\n\n## BASE DE DADOS (field: base_de_dados)\n```markdown\n{base_content}\n```"
        if "prompt_geral" in document_types and general_prompt_content.strip():
            docs_text += f"\n\n## PROMPT GERAL (field: prompt_geral)\n```markdown\n{general_prompt_content}\n```"

        if not docs_text.strip():
            return {
                "success": False,
                "error": "Nenhum documento com conteudo encontrado para os tipos selecionados.",
                "changes": [],
                "summary": ""
            }

        user_message = f"""PEDIDO DE EDICAO DO USUARIO:
{edit_request}

DOCUMENTOS DO CLIENTE:
{docs_text}

Gere as alteracoes necessarias em formato JSON conforme especificado."""

        # Call LLM
        self._report_progress("editing", 40, "AI generating edit changes")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        try:
            result = None
            provider = None
            metadata = {}
            last_error = None

            for attempt in range(2):
                response, provider, metadata = llm_manager.invoke_with_fallback(messages=messages)

                if metadata.get("usage"):
                    cost_tracker.track_usage(
                        provider=provider,
                        model=metadata.get("model", "unknown"),
                        agent_type="editor",
                        response_metadata=metadata,
                        job_id=job_id
                    )

                self._report_progress("parsing", 80, "Parsing AI response")

                content = response.content
                try:
                    result = parse_llm_json(content)
                    break
                except ValueError as e:
                    last_error = e
                    logger.warning(f"JSON parse failed (attempt {attempt + 1}/2), retrying: {e}")
                    if attempt == 0:
                        self._report_progress("editing", 50, "Resposta invalida, tentando novamente...")

            if result is None:
                raise last_error

            changes = result.get("changes", [])
            summary = result.get("summary", "")

            # Validate changes - ensure before text exists in documents
            validated_changes = []
            doc_map = {
                "prompt": prompt_content,
                "base_de_dados": base_content,
                "prompt_geral": general_prompt_content
            }

            for change in changes:
                field = change.get("field", "")
                before = change.get("before", "")
                doc_content = doc_map.get(field, "")

                if field not in doc_map:
                    logger.warning(f"Invalid field '{field}' in change, skipping")
                    continue

                if before and before.strip() in doc_content:
                    validated_changes.append(change)
                elif before:
                    # Try fuzzy match - first 50 chars
                    snippet = before.strip()[:50]
                    if snippet in doc_content:
                        validated_changes.append(change)
                    else:
                        logger.warning(f"Before text not found in {field}, including anyway: {before[:80]}...")
                        validated_changes.append(change)
                else:
                    validated_changes.append(change)

            self._report_progress("complete", 100, f"Generated {len(validated_changes)} changes")

            return {
                "success": True,
                "changes": validated_changes,
                "summary": summary,
                "provider": provider,
                "model": metadata.get("model")
            }

        except Exception as e:
            logger.error(f"Edit changes generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "changes": [],
                "summary": ""
            }

    def execute_workflow(
        self,
        document_content: str,
        document_type: str,
        max_iterations: int = 3,
        min_validation_score: int = 80,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> dict:
        """Legacy full-document editing workflow."""
        self._report_progress("initialization", 0, "Starting workflow")

        cleaned_content = document_processor.clean_document(document_content)
        analyzer = AnalyzerAgent()
        editor = EditorAgent()
        validator = ValidatorAgent()

        self._report_progress("analysis", 10, "Analyzing document")
        try:
            analysis = analyzer.analyze(
                document_content=cleaned_content, document_type=document_type,
                job_id=job_id, user_id=user_id, project_id=project_id
            )
        except Exception as e:
            return {"success": False, "error": "Analysis failed", "details": str(e)}

        if not analysis.get('issues'):
            self._report_progress("complete", 100, "No issues found")
            return {
                "success": True, "iterations": 0,
                "original_content": document_content, "edited_content": cleaned_content,
                "analysis": analysis,
                "final_validation": {"validation_passed": True, "overall_score": 100}
            }

        current_content = cleaned_content
        current_analysis = analysis
        edited_content = cleaned_content
        edit_result = {}
        validation = {}
        score = 0

        for iteration in range(1, max_iterations + 1):
            self._report_progress("editing", 20 + (iteration - 1) * 25, f"Iteration {iteration}: Editing")
            try:
                edit_result = editor.edit(
                    original_content=current_content, analysis=current_analysis,
                    document_type=document_type, job_id=job_id, user_id=user_id, project_id=project_id
                )
            except Exception as e:
                return {"success": False, "error": "Editing failed", "details": str(e)}

            edited_content = edit_result.get('edited_content', '')
            if not edited_content:
                break

            self._report_progress("validation", 35 + (iteration - 1) * 25, f"Iteration {iteration}: Validating")
            try:
                validation = validator.validate(
                    original_content=current_content, edited_content=edited_content,
                    analysis=current_analysis, document_type=document_type,
                    job_id=job_id, user_id=user_id, project_id=project_id
                )
            except Exception as e:
                return {"success": False, "error": "Validation failed", "details": str(e)}

            score = validation.get('overall_score', 0)
            if validation.get('validation_passed') and score >= min_validation_score:
                diff_result = markdown_processor.generate_line_diff(original=document_content, modified=edited_content)
                return {
                    "success": True, "iterations": iteration,
                    "original_content": document_content, "edited_content": edited_content,
                    "analysis": analysis, "edit_result": edit_result, "final_validation": validation,
                    "diff": diff_result['diff'], "statistics": diff_result['statistics']
                }

            remaining_critical = [p for p in validation.get('problems_remaining', []) if p.get('severity') == 'CRÍTICO']
            if remaining_critical and iteration < max_iterations:
                current_content = edited_content
                current_analysis = {"issues": validation.get('problems_remaining', []), "document_type": document_type}
            else:
                break

        diff_result = markdown_processor.generate_line_diff(original=document_content, modified=edited_content)
        return {
            "success": True, "iterations": iteration, "max_iterations_reached": True,
            "original_content": document_content, "edited_content": edited_content,
            "analysis": analysis, "edit_result": edit_result, "final_validation": validation,
            "diff": diff_result['diff'], "statistics": diff_result['statistics'],
            "warning": f"Score {score} below target {min_validation_score}"
        }

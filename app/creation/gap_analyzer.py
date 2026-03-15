"""
Gap Analyzer - Analyzes consolidated data against T3A standards.
Identifies missing sections and generates targeted questions.
"""

import json
import logging
import os
from dataclasses import dataclass, field

from app.llm.provider_manager import llm_manager
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

SECTIONS = [
    {"number": 0, "name": "Cabecalho", "max_questions": 2},
    {"number": 1, "name": "Identidade e Persona", "max_questions": 3},
    {"number": 2, "name": "Empresa e Informacoes", "max_questions": 3},
    {"number": 3, "name": "Fluxos de Atendimento", "max_questions": 5},
    {"number": 4, "name": "Regras", "max_questions": 3},
    {"number": 5, "name": "Protecao e Seguranca", "max_questions": 2},
    {"number": 6, "name": "Exemplos Praticos", "max_questions": 2},
    {"number": 7, "name": "Integracoes e APIs", "max_questions": 2},
]

INTEGRATION_KEYWORDS = ["ghl", "calendario", "crm", "webhook", "stripe", "zapier", "api", "integracao"]


@dataclass
class SectionGap:
    section_number: int
    section_name: str
    gap_level: str  # COMPLETE, PARTIAL, CRITICAL
    coverage_percent: int
    questions: list = field(default_factory=list)
    reasoning: str = ""


@dataclass
class GapAnalysisResult:
    sections: list = field(default_factory=list)
    total_questions: int = 0
    has_critical_gaps: bool = False
    summary: str = ""


def _load_templates() -> tuple[str, str]:
    """Load T3A template files."""
    templates_dir = os.path.join(BASE_DIR, "app", "creation", "templates_t3a")
    try:
        with open(os.path.join(templates_dir, "MANUAL_PROMPT_T3A.md"), 'r', encoding='utf-8') as f:
            manual = f.read()
        with open(os.path.join(templates_dir, "PADRAO_BASE_DE_DADOS.md"), 'r', encoding='utf-8') as f:
            padrao = f.read()
        return manual, padrao
    except Exception as e:
        logger.error(f"Failed to load templates: {e}")
        return "", ""


def analyze_section(section: dict, consolidated_text: str, manual: str, padrao: str) -> SectionGap:
    """Analyze a single section for gaps."""
    section_name = section["name"]
    max_q = section["max_questions"]

    # Skip integrations if no keywords found
    if section["number"] == 7:
        text_lower = consolidated_text.lower()
        if not any(kw in text_lower for kw in INTEGRATION_KEYWORDS):
            return SectionGap(
                section_number=section["number"], section_name=section_name,
                gap_level="COMPLETE", coverage_percent=100,
                reasoning="Nenhuma integracao detectada, secao nao aplicavel."
            )

    prompt = f"""Analise os dados coletados em relacao ESPECIFICAMENTE a secao "{section_name}" dos padroes T3A.
IMPORTANTE: Gere perguntas UNICAS e ESPECIFICAS para esta secao. NAO repita perguntas genericas como "qual o segmento" ou "qual a empresa" - essas sao de outras secoes.

PADRAO PROMPT T3A (secao relevante):
{manual[:3000]}

PADRAO BASE DE DADOS:
{padrao[:2000]}

DADOS COLETADOS:
{consolidated_text[:6000]}

Avalie a cobertura desta secao (0-100%) e gere perguntas para preencher lacunas.

Retorne APENAS JSON:
```json
{{
  "coverage_percent": 0-100,
  "reasoning": "explicacao da cobertura",
  "questions": ["pergunta 1", "pergunta 2"]
}}
```

Regras:
- Se cobertura >= 80%: nao gere perguntas
- Se 40-79%: maximo {min(max_q, 2)} perguntas
- Se < 40%: maximo {max_q} perguntas
- Perguntas devem ser especificas e direcionadas"""

    messages = [
        SystemMessage(content="Voce analisa dados contra padroes T3A. Retorne APENAS JSON valido."),
        HumanMessage(content=prompt)
    ]

    try:
        response, _, _ = llm_manager.invoke_with_fallback(messages=messages)
        content = response.content

        # Parse JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(content[json_start:json_end])
        else:
            data = {"coverage_percent": 50, "questions": [], "reasoning": "Nao foi possivel analisar"}

        coverage = min(100, max(0, int(data.get("coverage_percent", 50))))
        questions = data.get("questions", [])[:max_q]
        reasoning = data.get("reasoning", "")

        if coverage >= 80:
            gap_level = "COMPLETE"
            questions = []
        elif coverage >= 40:
            gap_level = "PARTIAL"
            questions = questions[:2]
        else:
            gap_level = "CRITICAL"

        return SectionGap(
            section_number=section["number"], section_name=section_name,
            gap_level=gap_level, coverage_percent=coverage,
            questions=questions, reasoning=reasoning
        )

    except Exception as e:
        logger.error(f"Gap analysis failed for {section_name}: {e}")
        return SectionGap(
            section_number=section["number"], section_name=section_name,
            gap_level="CRITICAL", coverage_percent=0,
            questions=[f"Nao foi possivel analisar a secao {section_name}. Descreva as informacoes desta area."],
            reasoning=f"Erro na analise: {str(e)}"
        )


def run_gap_analysis(consolidated_text: str) -> GapAnalysisResult:
    """Run gap analysis on all sections."""
    manual, padrao = _load_templates()
    sections = []

    for section_def in SECTIONS:
        logger.info(f"Analyzing section: {section_def['name']}")
        gap = analyze_section(section_def, consolidated_text, manual, padrao)
        sections.append(gap)

    # Deduplicate questions across sections
    seen_questions = set()
    for s in sections:
        unique = []
        for q in s.questions:
            q_normalized = q.lower().strip()[:80]
            if q_normalized not in seen_questions:
                seen_questions.add(q_normalized)
                unique.append(q)
        s.questions = unique

    total_questions = sum(len(s.questions) for s in sections)
    has_critical = any(s.gap_level == "CRITICAL" for s in sections)

    summary_parts = []
    for s in sections:
        icon = "✅" if s.gap_level == "COMPLETE" else ("⚠️" if s.gap_level == "PARTIAL" else "❌")
        summary_parts.append(f"{icon} {s.section_name}: {s.coverage_percent}% ({s.gap_level})")

    return GapAnalysisResult(
        sections=sections,
        total_questions=total_questions,
        has_critical_gaps=has_critical,
        summary="\n".join(summary_parts)
    )

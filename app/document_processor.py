"""
Document processor for cleaning and validation.
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass

from app.utils.markdown_utils import markdown_processor

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    client_name: Optional[str] = None
    document_type: Optional[str] = None


class DocumentProcessor:
    def __init__(self):
        self.markdown = markdown_processor

    def clean_document(self, content: str) -> str:
        return self.markdown.clean_document(content)

    def validate_prompt_structure(self, content: str) -> dict:
        sections = self.markdown.extract_sections(content)
        required_sections = ["IDENTIDADE", "PERSONA", "EMPRESA", "FLUXO", "REGRAS", "PROTEÇÃO", "EXEMPLO"]
        found_sections = set()
        for section in sections:
            title_normalized = section.title.upper()
            for required in required_sections:
                if required in title_normalized:
                    found_sections.add(required)
        missing = set(required_sections) - found_sections
        issues = [{"type": "error", "section": s, "message": f"Seção obrigatória ausente: {s}"} for s in missing]
        markdown_validation = self.markdown.validate_markdown_structure(content)
        issues.extend(markdown_validation["issues"])
        return {
            "valid": len(missing) == 0 and markdown_validation["valid"],
            "found_sections": list(found_sections),
            "missing_sections": list(missing),
            "issues": issues
        }

    def validate_database_structure(self, content: str) -> dict:
        sections = self.markdown.extract_sections(content)
        required_sections = ["INFORMAÇÕES DA EMPRESA", "PRODUTOS", "SERVIÇOS", "OBJEÇÕES", "DÚVIDAS FREQUENTES", "POLÍTICAS"]
        found_sections = set()
        for section in sections:
            title_normalized = section.title.upper()
            for required in required_sections:
                if required in title_normalized:
                    found_sections.add(required)
        missing = set(required_sections) - found_sections
        issues = [{"type": "error", "section": s, "message": f"Seção obrigatória ausente: {s}"} for s in missing]
        markdown_validation = self.markdown.validate_markdown_structure(content)
        issues.extend(markdown_validation["issues"])
        return {
            "valid": len(missing) == 0 and markdown_validation["valid"],
            "found_sections": list(found_sections),
            "missing_sections": list(missing),
            "issues": issues
        }


document_processor = DocumentProcessor()

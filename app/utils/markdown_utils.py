"""
Markdown utilities for document processing.
"""

import re
import logging
import difflib
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentSection:
    title: str
    level: int
    content: str
    start_line: int
    end_line: int


class MarkdownProcessor:
    def clean_document(self, content: str) -> str:
        cleaned = re.sub(r'\\([#*_\[\]()])', r'\1', content)
        cleaned = re.sub(r'\\/', '', cleaned)
        cleaned = re.sub(r'\\+', r'\\', cleaned)
        lines = [line.rstrip() for line in cleaned.split('\n')]
        cleaned = '\n'.join(lines)
        cleaned = cleaned.replace('\r\n', '\n')
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def extract_sections(self, content: str) -> list[DocumentSection]:
        sections = []
        lines = content.split('\n')
        current_section = None
        section_content_lines = []

        for i, line in enumerate(lines, start=1):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                if current_section:
                    current_section.content = '\n'.join(section_content_lines).strip()
                    current_section.end_line = i - 1
                    sections.append(current_section)
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = DocumentSection(title=title, level=level, content="", start_line=i, end_line=i)
                section_content_lines = []
            else:
                if current_section:
                    section_content_lines.append(line)

        if current_section:
            current_section.content = '\n'.join(section_content_lines).strip()
            current_section.end_line = len(lines)
            sections.append(current_section)

        return sections

    def generate_diff(self, original: str, modified: str) -> str:
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        differ = difflib.Differ()
        diff = list(differ.compare(original_lines, modified_lines))
        formatted_lines = []
        for line in diff:
            if line.startswith('- '):
                formatted_lines.append(f"- {line[2:]}")
            elif line.startswith('+ '):
                formatted_lines.append(f"+ {line[2:]}")
            elif line.startswith('  '):
                formatted_lines.append(f"  {line[2:]}")
        return '\n'.join(formatted_lines)

    def generate_line_diff(self, original: str, modified: str) -> dict:
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')

        additions = 0
        deletions = 0
        diff_lines = list(difflib.unified_diff(original_lines, modified_lines, lineterm=''))
        for line in diff_lines:
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1

        return {
            "diff": self.generate_diff(original, modified),
            "statistics": {
                "original_lines": len(original_lines),
                "modified_lines": len(modified_lines),
                "additions": additions,
                "deletions": deletions,
                "changes": additions + deletions
            }
        }

    def validate_markdown_structure(self, content: str) -> dict:
        issues = []
        sections = self.extract_sections(content)
        if not content.strip():
            issues.append({"type": "error", "message": "Document is empty"})
        if not sections:
            issues.append({"type": "warning", "message": "No sections found in document"})
        return {
            "valid": len([i for i in issues if i["type"] == "error"]) == 0,
            "sections_count": len(sections),
            "issues": issues
        }


markdown_processor = MarkdownProcessor()

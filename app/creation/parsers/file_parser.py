"""
File parsers for upload processing.
Supports PDF, DOCX, TXT, CSV, WhatsApp exports.
"""

import re
import os
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    filename: str
    file_type: str
    text: str
    is_whatsapp: bool = False
    warnings: list = field(default_factory=list)


def detect_whatsapp(text: str) -> bool:
    """Detect if text is a WhatsApp export."""
    pattern = r'\[\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}'
    matches = re.findall(pattern, text[:5000])
    return len(matches) >= 3


def parse_txt(filepath: str, filename: str) -> ParseResult:
    """Parse text file, detecting WhatsApp exports."""
    for encoding in ['utf-8', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        text = open(filepath, 'r', encoding='utf-8', errors='replace').read()

    is_wa = detect_whatsapp(text)
    return ParseResult(filename=filename, file_type="whatsapp" if is_wa else "text",
                       text=text, is_whatsapp=is_wa)


def parse_pdf(filepath: str, filename: str) -> ParseResult:
    """Parse PDF file."""
    try:
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"--- Pagina {i+1} ---\n{text}")
            text = "\n\n".join(pages)
            if len(text.strip()) < 100:
                return ParseResult(filename=filename, file_type="pdf", text=text,
                                   warnings=["PDF possivelmente escaneado, pouco texto extraido"])
            return ParseResult(filename=filename, file_type="pdf", text=text)
    except Exception as e:
        return ParseResult(filename=filename, file_type="pdf", text="",
                           warnings=[f"Erro ao processar PDF: {str(e)}"])


def parse_docx(filepath: str, filename: str) -> ParseResult:
    """Parse DOCX file."""
    try:
        import docx
        doc = docx.Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        return ParseResult(filename=filename, file_type="docx", text=text)
    except Exception as e:
        return ParseResult(filename=filename, file_type="docx", text="",
                           warnings=[f"Erro ao processar DOCX: {str(e)}"])


def parse_file(filepath: str, filename: str) -> ParseResult:
    """Parse any supported file."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        return parse_pdf(filepath, filename)
    elif ext in ('.docx', '.doc'):
        return parse_docx(filepath, filename)
    elif ext in ('.txt', '.csv'):
        return parse_txt(filepath, filename)
    else:
        return ParseResult(filename=filename, file_type="unknown", text="",
                           warnings=[f"Formato nao suportado: {ext}"])

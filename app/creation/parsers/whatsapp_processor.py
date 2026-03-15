"""
WhatsApp export processor.
Handles ZIP files with WhatsApp conversations.
Extracts text from .txt files, detects WhatsApp format.
Note: Audio/image files are logged as metadata but not transcribed in this version.
"""

import re
import os
import zipfile
import logging
from collections import Counter

logger = logging.getLogger(__name__)

WA_PATTERN = re.compile(
    r'^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[-–]\s*([^:]+):\s*(.+)$'
)

SYSTEM_KEYWORDS = [
    "adicionou", "removeu", "saiu", "entrou", "criou", "alterou",
    "mensagens e chamadas", "criptografia", "added", "removed", "left", "joined"
]

MEDIA_MARKERS = ["<Mídia oculta>", "<Media omitted>", ".opus", ".jpg", ".mp4", ".png", ".webp"]


def is_whatsapp_text(text: str) -> bool:
    """Detect if text is a WhatsApp export."""
    lines = text.split('\n')[:10]
    matches = sum(1 for line in lines if WA_PATTERN.match(line.strip()))
    return matches >= 2


def parse_whatsapp_text(text: str) -> dict:
    """Parse WhatsApp text and extract structured data."""
    lines = text.split('\n')
    messages = []
    participants = Counter()
    questions = []

    for line in lines:
        match = WA_PATTERN.match(line.strip())
        if not match:
            continue

        date, time, sender, content = match.groups()
        sender = sender.strip()
        content = content.strip()

        # Skip system messages
        if any(kw in content.lower() for kw in SYSTEM_KEYWORDS):
            continue

        # Detect media
        is_media = any(m in content for m in MEDIA_MARKERS)

        participants[sender] += 1

        if not is_media:
            messages.append({"sender": sender, "content": content})
            if content.endswith("?") and len(content) > 10:
                questions.append(content)

    # Identify roles
    if participants:
        sorted_p = participants.most_common()
        attendant = sorted_p[0][0] if sorted_p else "Desconhecido"
        lead = sorted_p[1][0] if len(sorted_p) > 1 else "Desconhecido"
    else:
        attendant = lead = "Desconhecido"

    # Detect tone
    formal_score = 0
    for msg in messages:
        if msg["sender"] == attendant:
            txt = msg["content"].lower()
            if any(w in txt for w in ["bom dia", "boa tarde", "boa noite", "você", "senhor"]):
                formal_score += 1
            if any(w in txt for w in ["vc", "tb", "tbm", "blz", "vlw"]):
                formal_score -= 1

    tone = "formal" if formal_score > 3 else ("casual" if formal_score < -1 else "semiformal")

    # Build conversation text
    conv_text = "\n".join(f"[{m['sender']}]: {m['content']}" for m in messages)

    metadata = {
        "total_messages": len(messages),
        "participants": dict(participants),
        "attendant": attendant,
        "lead": lead,
        "tone": tone,
        "questions_count": len(questions),
        "media_count": sum(1 for line in text.split('\n') if any(m in line for m in MEDIA_MARKERS))
    }

    return {
        "text": conv_text,
        "metadata": metadata,
        "questions": questions[:20]
    }


def process_whatsapp_zip(zip_path: str) -> str:
    """Process a WhatsApp export ZIP file. Returns extracted conversation text."""
    all_conversations = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            txt_files = [f for f in zf.namelist()
                         if f.endswith('.txt') and not f.startswith('__MACOSX')]

            media_files = [f for f in zf.namelist()
                          if any(f.lower().endswith(ext) for ext in
                                 ['.opus', '.mp3', '.wav', '.ogg', '.jpg', '.jpeg', '.png', '.mp4', '.webp'])]

            logger.info(f"ZIP contains {len(txt_files)} text files, {len(media_files)} media files")

            for txt_file in txt_files:
                try:
                    raw = zf.read(txt_file)
                    # Try UTF-8, fallback to Latin-1
                    for enc in ['utf-8', 'latin-1']:
                        try:
                            text = raw.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        text = raw.decode('utf-8', errors='replace')

                    if is_whatsapp_text(text):
                        result = parse_whatsapp_text(text)
                        meta = result["metadata"]
                        header = (f"## Conversa WhatsApp: {meta['attendant']} <> {meta['lead']}\n"
                                  f"Total mensagens: {meta['total_messages']} | Tom: {meta['tone']} | "
                                  f"Midias: {meta['media_count']}\n\n")
                        all_conversations.append(header + result["text"])
                    else:
                        all_conversations.append(f"## Arquivo: {txt_file}\n\n{text[:5000]}")
                except Exception as e:
                    logger.warning(f"Failed to process {txt_file}: {e}")

            if media_files:
                media_summary = f"\n\n## Midias encontradas ({len(media_files)} arquivos)\n"
                audio_count = sum(1 for f in media_files if any(f.lower().endswith(e) for e in ['.opus', '.mp3', '.wav', '.ogg']))
                image_count = sum(1 for f in media_files if any(f.lower().endswith(e) for e in ['.jpg', '.jpeg', '.png', '.webp']))
                video_count = sum(1 for f in media_files if f.lower().endswith('.mp4'))
                media_summary += f"- Audios: {audio_count}\n- Imagens: {image_count}\n- Videos: {video_count}\n"
                all_conversations.append(media_summary)

    except Exception as e:
        logger.error(f"Failed to process ZIP: {e}")
        return f"Erro ao processar ZIP: {str(e)}"

    return "\n\n---\n\n".join(all_conversations) if all_conversations else "Nenhuma conversa WhatsApp encontrada no ZIP."

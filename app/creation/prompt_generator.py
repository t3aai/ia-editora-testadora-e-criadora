"""
Prompt Generator - Generates PROMPT_CLIENTE and BASE_DE_DADOS from consolidated data.
Uses Claude Sonnet with T3A templates as reference.
"""

import logging
import os

from app.llm.provider_manager import llm_manager
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _load_template(name: str) -> str:
    """Load a T3A template file."""
    path = os.path.join(BASE_DIR, "app", "creation", "templates_t3a", name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def generate_prompt_cliente(consolidated_text: str, gap_answers: str = "") -> str:
    """Generate PROMPT_CLIENTE markdown."""
    manual = _load_template("MANUAL_PROMPT_T3A.md")[:6000]

    system_prompt = f"""Voce e um especialista em criacao de prompts de chatbot para atendimento via WhatsApp seguindo o padrao T3A.

# MANUAL DE REFERENCIA T3A (estrutura obrigatoria):
{manual}

# REGRAS CRITICAS:
1. Siga a estrutura do manual T3A EXATAMENTE
2. NUNCA invente informacoes da empresa - use [A PREENCHER] quando faltar dados
3. Secao 3 (Fluxos) e a mais critica: minimo 3 etapas, maximo 7
4. speech: false e o padrao
5. Mensagens numeradas: "Mensagem 1:", "Mensagem 2:"
6. Apos cada pergunta: "(Aguardar a resposta do lead)"
7. Ramificacoes = numeros (1,2,3), variacoes = letras (A,B,C)
8. Cada etapa termina com "Proximo passo: Seguir para etapa X"
9. Use markdown valido e bem formatado
10. Gere o prompt COMPLETO, nao parcial"""

    user_message = f"""Com base nos dados coletados, gere o PROMPT_CLIENTE completo em markdown:

DADOS COLETADOS:
{consolidated_text[:10000]}

{f'RESPOSTAS ADICIONAIS DO USUARIO:{chr(10)}{gap_answers[:5000]}' if gap_answers else ''}

Gere o prompt completo agora."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]

    try:
        response, _, _ = llm_manager.invoke_with_fallback(messages=messages)
        return response.content
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        return f"# ERRO NA GERACAO\n\nNao foi possivel gerar o prompt: {str(e)}"


def generate_base_dados(consolidated_text: str, gap_answers: str = "") -> str:
    """Generate BASE_DE_DADOS markdown."""
    padrao = _load_template("PADRAO_BASE_DE_DADOS.md")[:8000]

    system_prompt = f"""Voce e um especialista em criacao de bases de dados para chatbots de atendimento T3A.

# PADRAO BASE DE DADOS T3A (estrutura obrigatoria):
{padrao}

# REGRAS CRITICAS:
1. NUNCA invente precos, enderecos, telefones - use [A PREENCHER]
2. Siga a estrutura markdown do padrao EXATAMENTE
3. Inclua TODAS as secoes: Empresa, Produtos, Objecoes, FAQ, Politicas, Processos, Avisos, Controle
4. Objecoes devem ter 4 categorias: Preco, Necessidade, Confianca, Timing
5. Cada objecao: "O que dizer" + "O que NAO fazer"
6. FAQ: minimo 7 categorias
7. Use tabelas markdown quando apropriado
8. Gere a base COMPLETA"""

    user_message = f"""Com base nos dados coletados, gere a BASE_DE_DADOS completa em markdown:

DADOS COLETADOS:
{consolidated_text[:10000]}

{f'RESPOSTAS ADICIONAIS DO USUARIO:{chr(10)}{gap_answers[:5000]}' if gap_answers else ''}

Gere a base de dados completa agora."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]

    try:
        response, _, _ = llm_manager.invoke_with_fallback(messages=messages)
        return response.content
    except Exception as e:
        logger.error(f"Base generation failed: {e}")
        return f"# ERRO NA GERACAO\n\nNao foi possivel gerar a base: {str(e)}"

"""
Test Simulator - Simulates chatbot conversations using the client's prompt/base.
Supports multiple LLM providers for realistic testing.
"""

import json
import logging
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings

logger = logging.getLogger(__name__)


def get_test_llm(model_choice: str):
    """Get LLM instance for testing based on model choice."""
    if model_choice == "deepseek":
        return ChatOpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=2048
        )
    elif model_choice == "gpt":
        return ChatOpenAI(
            api_key=settings.openai_test_api_key or settings.openai_api_key,
            model="gpt-4.1",
            temperature=0.3,
            max_tokens=2048
        )
    elif model_choice == "claude":
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,
            max_tokens=2048
        )
    else:
        raise ValueError(f"Unknown model: {model_choice}")


def generate_test_scenario(change_section: str, change_reason: str, change_after: str,
                          prompt_content: str, base_content: str) -> list[dict]:
    """
    Generate a test conversation scenario based on the edited section.
    Uses the editor LLM to create realistic test messages.
    """
    from app.llm.provider_manager import llm_manager

    scenario_prompt = f"""Gere um cenario de teste CURTO (3-4 mensagens de lead) para testar a seguinte alteracao num chatbot de atendimento:

Secao editada: {change_section}
Motivo da edicao: {change_reason}
Novo conteudo: {change_after[:500]}

Gere mensagens realistas que um lead enviaria para testar especificamente essa parte do fluxo.
Retorne APENAS JSON:

```json
{{
  "scenario_name": "nome curto do cenario",
  "messages": [
    {{"role": "lead", "content": "mensagem do lead"}},
    {{"role": "lead", "content": "segunda mensagem"}},
    {{"role": "lead", "content": "terceira mensagem"}}
  ]
}}
```"""

    messages = [
        SystemMessage(content="Voce gera cenarios de teste para chatbots. Retorne APENAS JSON valido."),
        HumanMessage(content=scenario_prompt)
    ]

    try:
        response, _, _ = llm_manager.invoke_with_fallback(messages=messages)
        content = response.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            result = json.loads(content[json_start:json_end])
            return result.get("messages", [])
    except Exception as e:
        logger.error(f"Failed to generate scenario: {e}")

    # Fallback: generic test messages
    return [
        {"role": "lead", "content": "Oi, tudo bem?"},
        {"role": "lead", "content": "Quero saber mais sobre seus produtos"},
        {"role": "lead", "content": "Qual o preco?"}
    ]


def simulate_conversation(
    prompt_content: str,
    base_content: str,
    general_prompt_content: str,
    lead_messages: list[dict],
    model_choice: str = "deepseek"
) -> list[dict]:
    """
    Simulate a full conversation between a lead and the chatbot.
    The chatbot uses the client's prompt+base+geral as system prompt.
    """
    # Build system prompt from client docs
    system_parts = [
        "INSTRUCAO IMPORTANTE: Voce e um chatbot de atendimento via WhatsApp. "
        "Responda APENAS com texto natural de conversa, como uma pessoa real responderia no WhatsApp. "
        "NAO use formatos como JSON, STAGE, TEXTO, speech, arrays ou qualquer estrutura tecnica. "
        "Responda com mensagens curtas e naturais, como se estivesse no WhatsApp. "
        "Use o prompt e base de dados abaixo como referencia para CONTEUDO, mas o FORMATO da resposta deve ser texto puro conversacional.\n\n"
    ]
    if general_prompt_content and general_prompt_content.strip():
        system_parts.append(general_prompt_content.strip())
    if prompt_content and prompt_content.strip():
        system_parts.append(prompt_content.strip())
    if base_content and base_content.strip():
        system_parts.append(f"\n\n# BASE DE DADOS\n\n{base_content.strip()}")

    system_prompt = "\n\n".join(system_parts)
    if not system_prompt.strip():
        return [{"role": "system", "content": "Erro: nenhum prompt/base configurado para simular."}]

    try:
        llm = get_test_llm(model_choice)
    except Exception as e:
        return [{"role": "system", "content": f"Erro ao inicializar modelo {model_choice}: {str(e)}"}]

    conversation = []
    messages = [SystemMessage(content=system_prompt)]

    for lead_msg in lead_messages:
        lead_text = lead_msg.get("content", "")
        conversation.append({"role": "lead", "content": lead_text})
        messages.append(HumanMessage(content=lead_text))

        try:
            response = llm.invoke(messages)
            bot_text = response.content
            conversation.append({"role": "bot", "content": bot_text})
            messages.append(AIMessage(content=bot_text))
        except Exception as e:
            conversation.append({"role": "bot", "content": f"[Erro: {str(e)}]"})
            break

    return conversation


def run_change_test(
    change: dict,
    client_prompt: str,
    client_base: str,
    client_geral: str,
    model_choice: str = "deepseek"
) -> dict:
    """
    Run a complete test for a specific change.
    1. Apply the change to get the edited docs
    2. Generate test scenario for the changed section
    3. Simulate conversation with the edited docs
    """
    # Apply the change to the relevant document
    field = change.get("field", "prompt")
    before = change.get("before_text", "")
    after = change.get("after_text", "")

    edited_prompt = client_prompt
    edited_base = client_base
    edited_geral = client_geral

    if field == "prompt" and before.strip() in client_prompt:
        edited_prompt = client_prompt.replace(before.strip(), after, 1)
    elif field == "base_de_dados" and before.strip() in client_base:
        edited_base = client_base.replace(before.strip(), after, 1)
    elif field == "prompt_geral" and before.strip() in client_geral:
        edited_geral = client_geral.replace(before.strip(), after, 1)

    # Generate test scenario
    lead_messages = generate_test_scenario(
        change_section=change.get("section", ""),
        change_reason=change.get("reason", ""),
        change_after=after,
        prompt_content=edited_prompt,
        base_content=edited_base
    )

    # Simulate conversation
    conversation = simulate_conversation(
        prompt_content=edited_prompt,
        base_content=edited_base,
        general_prompt_content=edited_geral,
        lead_messages=lead_messages,
        model_choice=model_choice
    )

    return {
        "model": model_choice,
        "conversation": conversation,
        "scenario_messages": len(lead_messages)
    }

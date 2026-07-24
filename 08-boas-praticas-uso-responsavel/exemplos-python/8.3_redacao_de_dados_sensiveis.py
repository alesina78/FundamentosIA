"""Remove/mascara dados sensíveis ANTES de enviar texto para uma API de terceiros
(LLM ou qualquer outra). Abordagem baseada em regex simples — para produção, considere
uma biblioteca dedicada de detecção de PII (ex: Microsoft Presidio), que cobre muito
mais casos e idiomas do que este exemplo didático."""
import re

import anthropic

client = anthropic.Anthropic()

PADROES_SENSIVEIS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "CPF": re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"),
    "TELEFONE": re.compile(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"),
    "CARTAO_CREDITO": re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}"),
}


def redigir_dados_sensiveis(texto: str) -> str:
    """Substitui cada padrão sensível encontrado por um placeholder identificável."""
    texto_redigido = texto
    for tipo, padrao in PADROES_SENSIVEIS.items():
        texto_redigido = padrao.sub(f"[{tipo}_REDIGIDO]", texto_redigido)
    return texto_redigido


if __name__ == "__main__":
    ticket_cliente = """\
Olá, meu nome é João. Meu email é joao.silva@email.com e meu CPF é 529.982.247-25.
Comprei um produto com o cartão 4111 1111 1111 1111 e ele veio com defeito. Podem
me ligar no (11) 98765-4321?
"""

    ticket_seguro = redigir_dados_sensiveis(ticket_cliente)
    print("--- Texto após redação ---")
    print(ticket_seguro)

    # Só o texto SEM dados sensíveis é enviado para a API externa.
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Resuma o problema relatado neste ticket de suporte:\n\n{ticket_seguro}",
        }],
    )
    print("\n--- Resumo gerado (sem nunca expor os dados sensíveis à API) ---")
    print(r.content[0].text)

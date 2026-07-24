"""Um padrão simples de 'human-in-the-loop': o LLM processa a tarefa e também
avalia sua própria confiança; respostas de baixa confiança ou em categorias
sensíveis são roteadas para revisão humana antes de qualquer ação ser tomada."""
import json

import anthropic

client = anthropic.Anthropic()

CATEGORIAS_SEMPRE_REVISADAS = {"reembolso_alto_valor", "reclamacao_juridica", "dado_sensivel"}


def classificar_ticket(texto_ticket: str) -> dict:
    prompt = f"""\
Classifique o ticket de suporte abaixo. Responda em JSON com os campos:
- categoria: uma de "duvida_simples", "reembolso_baixo_valor", "reembolso_alto_valor",
  "reclamacao_juridica", "dado_sensivel"
- confianca: sua confiança na classificação, de 0 a 1
- resposta_sugerida: uma resposta sugerida ao cliente, em 1-2 frases

Ticket: {texto_ticket}

Responda apenas com o JSON, sem texto adicional.
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(r.content[0].text)


def processar_ticket(texto_ticket: str, limiar_confianca: float = 0.8) -> dict:
    classificacao = classificar_ticket(texto_ticket)

    precisa_revisao_humana = (
        classificacao["categoria"] in CATEGORIAS_SEMPRE_REVISADAS
        or classificacao["confianca"] < limiar_confianca
    )

    return {
        **classificacao,
        "acao": "enviar_para_revisao_humana" if precisa_revisao_humana else "responder_automaticamente",
    }


if __name__ == "__main__":
    tickets = [
        "Meu pedido chegou 2 dias atrasado, quando devo esperar a entrega?",
        "Quero um reembolso de R$8.500 e vou acionar meu advogado se não for atendido.",
    ]

    for ticket in tickets:
        resultado = processar_ticket(ticket)
        print(f"Ticket: {ticket[:60]}...")
        print(f"  -> {resultado['acao']} (categoria: {resultado['categoria']}, "
              f"confiança: {resultado['confianca']})")

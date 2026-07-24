"""Usa o próprio LLM para revisar uma especificação ANTES de implementar — pedindo
para ele apontar ambiguidades, casos de borda não cobertos e perguntas em aberto.
Essa etapa de revisão custa poucos tokens e pode evitar retrabalho na implementação."""
import anthropic

client = anthropic.Anthropic()

spec_com_lacunas = """\
Função: aplicar_desconto(preco: float, percentual_desconto: float) -> float

Aplica um desconto percentual sobre um preço e retorna o novo preço.
"""


def revisar_spec(spec: str) -> str:
    prompt = f"""\
Você é um revisor técnico. Analise a especificação abaixo e liste:
1. Ambiguidades — pontos que podem ser interpretados de mais de uma forma.
2. Casos de borda não cobertos — o que acontece com valores extremos ou inválidos?
3. Perguntas que você faria ao autor antes de implementar.

Não implemente nada — apenas revise a especificação.

Especificação:
{spec}
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


if __name__ == "__main__":
    print(revisar_spec(spec_com_lacunas))

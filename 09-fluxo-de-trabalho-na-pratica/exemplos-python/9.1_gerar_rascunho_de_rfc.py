"""Usa IA para transformar uma ideia informal num rascunho estruturado de RFC/design
doc — um ponto de partida para discussão, não um documento final. A revisão e decisão
continuam sendo do time (ver módulo 7, sobre specs, e módulo 8.4, revisão humana)."""
import anthropic

client = anthropic.Anthropic()

ideia_informal = """\
A gente precisa de um jeito de cachear as respostas da nossa API de busca porque
está caro e lento chamar toda vez. Queria algo simples, que não precise adicionar
mais um serviço na infra se der pra evitar.
"""


def gerar_rascunho_rfc(ideia: str) -> str:
    prompt = f"""\
Você é um engenheiro de software sênior ajudando a estruturar uma ideia em um rascunho
de RFC (design doc) para revisão do time. Use este formato:

## Problema
## Objetivo (o que resolve, especificamente)
## Não-objetivos (o que fica de fora dessa proposta)
## Proposta (2-3 abordagens possíveis, com trade-offs)
## Perguntas em aberto (o que precisa ser decidido pelo time antes de prosseguir)

Ideia informal do autor:
{ideia}

Importante: isso é um RASCUNHO para discussão, não uma decisão final. Sinalize
claramente as perguntas em aberto — não presuma respostas que o time ainda não deu.
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


if __name__ == "__main__":
    print(gerar_rascunho_rfc(ideia_informal))

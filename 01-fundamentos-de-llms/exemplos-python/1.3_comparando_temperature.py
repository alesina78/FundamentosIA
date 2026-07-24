import anthropic

client = anthropic.Anthropic()


def perguntar(pergunta: str, temperature: float = 1.0) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        temperature=temperature,
        messages=[{"role": "user", "content": pergunta}],
    )
    return r.content[0].text


pergunta = "Qual foi o placar da final de um campeonato fictício que não existe?"
print(perguntar(pergunta))
# Um LLM mal orientado pode "inventar" um placar em vez de dizer que não existe informação.

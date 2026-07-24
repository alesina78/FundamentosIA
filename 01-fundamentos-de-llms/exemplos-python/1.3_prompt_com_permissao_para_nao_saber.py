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


# Continuação de 1.3_comparando_temperature.py: um prompt melhor reduz (mas não
# elimina) o risco de alucinação.
pergunta_melhor = (
    "Qual foi o placar da final de um campeonato fictício que não existe? "
    "Se você não tiver certeza ou a informação não existir, diga explicitamente "
    "que não sabe, em vez de inventar uma resposta."
)
print(perguntar(pergunta_melhor, temperature=0))

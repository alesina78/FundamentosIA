import anthropic

client = anthropic.Anthropic()


def perguntar(prompt: str) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


# Prompt fraco: vago, sem contexto, sem formato de saída definido.
prompt_fraco = "Escreva sobre marketing."
print("--- Prompt fraco ---")
print(perguntar(prompt_fraco))

# Prompt forte: instrução clara, contexto, formato de saída explícito.
prompt_forte = """\
Você é um consultor de marketing para pequenas empresas.

Contexto: uma cafeteria de bairro quer aumentar o movimento às terças e quartas-feiras,
dias historicamente fracos.

Tarefa: sugira 3 ações de marketing de baixo custo, específicas para esse cenário.

Formato de saída: lista numerada, cada item com no máximo 2 frases.
"""
print("\n--- Prompt forte ---")
print(perguntar(prompt_forte))

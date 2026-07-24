import anthropic

client = anthropic.Anthropic()


def perguntar(prompt: str, max_tokens: int = 300) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


# --- Few-shot: mostrar exemplos do padrão esperado em vez de só descrever ---
prompt_few_shot = """\
Classifique o sentimento de cada avaliação como "positivo", "negativo" ou "neutro".

Avaliação: "Entrega rápida, produto exatamente como descrito."
Sentimento: positivo

Avaliação: "Chegou quebrado e o suporte não respondeu."
Sentimento: negativo

Avaliação: "Produto ok, nada excepcional, mas cumpre o que promete."
Sentimento: neutro

Avaliação: "Melhor compra que fiz esse ano, super recomendo!"
Sentimento:"""

print("--- Few-shot ---")
print(perguntar(prompt_few_shot, max_tokens=10))


# --- Chain-of-thought: pedir para o modelo raciocinar passo a passo ---
prompt_sem_cot = "Uma loja vende 3 produtos: A custa R$45, B custa R$30 e C custa R$15. \
Um cliente compra 2 unidades de A, 1 de B e 4 de C. Qual o total da compra?"

prompt_com_cot = prompt_sem_cot + \
    "\n\nPense passo a passo antes de dar a resposta final."

print("\n--- Sem chain-of-thought ---")
print(perguntar(prompt_sem_cot))

print("\n--- Com chain-of-thought ---")
print(perguntar(prompt_com_cot))

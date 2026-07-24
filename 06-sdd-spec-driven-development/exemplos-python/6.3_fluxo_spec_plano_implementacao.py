"""Fluxo completo spec -> plano -> implementação -> verificação, cada etapa uma
chamada de API separada e focada — o padrão que harnesses de agentic coding (módulo 7)
automatizam, mas que você pode reproduzir manualmente com chamadas simples."""
import anthropic

client = anthropic.Anthropic()

spec = """\
Função: aplicar_desconto(preco: float, percentual_desconto: float) -> float

Regras:
1. percentual_desconto deve estar entre 0 e 100 (inclusive). Fora disso, lançar ValueError.
2. preco deve ser maior ou igual a 0. Caso contrário, lançar ValueError.
3. O resultado deve ser arredondado para 2 casas decimais.

Casos de teste:
- aplicar_desconto(100.0, 10) -> 90.0
- aplicar_desconto(50.0, 0) -> 50.0
- aplicar_desconto(50.0, 100) -> 0.0
- aplicar_desconto(50.0, 150) -> ValueError
- aplicar_desconto(-10.0, 10) -> ValueError
"""


def perguntar(prompt: str, max_tokens: int = 600) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


# 1. PLANO: antes de escrever código, pedir um plano de implementação a partir da spec.
plano = perguntar(f"""\
Com base na especificação abaixo, descreva em bullet points o plano de implementação
(estrutura da função, validações, ordem das operações). Não escreva código ainda.

{spec}
""")
print("=== Plano ===")
print(plano)

# 2. IMPLEMENTAÇÃO: gerar o código a partir da spec + plano aprovado.
codigo = perguntar(f"""\
Implemente a função Python a seguir, seguindo exatamente esta especificação e este plano.
Retorne APENAS o código, sem explicação.

Especificação:
{spec}

Plano:
{plano}
""")
print("\n=== Código gerado ===")
print(codigo)

# 3. VERIFICAÇÃO: pedir para o próprio modelo checar se a implementação cobre os casos
# de teste da spec — uma verificação leve antes de rodar testes de verdade.
verificacao = perguntar(f"""\
Verifique se o código abaixo atende TODOS os casos de teste da especificação. Para cada
caso de teste, diga se o código passaria ou falharia, e por quê.

Especificação:
{spec}

Código:
{codigo}
""")
print("\n=== Verificação ===")
print(verificacao)

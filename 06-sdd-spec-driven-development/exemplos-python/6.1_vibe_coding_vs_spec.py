"""Compara o resultado de pedir código direto ("vibe coding") vs. pedir a partir de
uma especificação estruturada — mesmo pedido de negócio, prompts diferentes."""
import anthropic

client = anthropic.Anthropic()


def gerar_codigo(prompt: str) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


# "Vibe coding": pedido vago, sem definir regras de negócio, formato de erro, limites.
prompt_vibe = "Crie uma função Python para validar CPF."

# Spec-driven: a especificação define entrada, saída, regras e casos de erro
# ANTES de pedir a implementação — reduz o espaço de interpretação do modelo.
spec = """\
Função: validar_cpf(cpf: str) -> bool

Entrada: string contendo um CPF, pode vir com ou sem formatação (pontos e traço).

Regras:
1. Remover caracteres não numéricos antes de validar.
2. CPF deve ter exatamente 11 dígitos após a limpeza.
3. Rejeitar CPFs com todos os dígitos iguais (ex: "11111111111") — são inválidos
   mesmo passando no cálculo do dígito verificador.
4. Validar os dois dígitos verificadores segundo o algoritmo oficial da Receita Federal.

Saída: True se válido, False caso contrário. Não deve lançar exceção para entrada
malformada — apenas retornar False.

Casos de teste esperados:
- validar_cpf("529.982.247-25") -> True
- validar_cpf("11111111111") -> False
- validar_cpf("123") -> False
- validar_cpf("abc") -> False
"""
prompt_spec_driven = f"Implemente a função Python a seguir, exatamente conforme a especificação:\n\n{spec}"


if __name__ == "__main__":
    print("=== Vibe coding (prompt vago) ===")
    print(gerar_codigo(prompt_vibe))

    print("\n\n=== Spec-driven (especificação clara) ===")
    print(gerar_codigo(prompt_spec_driven))

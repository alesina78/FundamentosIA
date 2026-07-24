"""Boas práticas para IA na escrita de código: pedir mudanças incrementais e
justificadas, nunca um código enorme de uma vez sem entender o que mudou."""
import anthropic

client = anthropic.Anthropic()

codigo_atual = '''\
def calcular_frete(peso_kg: float, distancia_km: float) -> float:
    return peso_kg * distancia_km * 0.5
'''

pedido = "Adicione frete grátis para pedidos com peso menor que 1kg e distância menor que 10km."


def pedir_mudanca_com_justificativa(codigo: str, pedido: str) -> str:
    prompt = f"""\
Código atual:
```python
{codigo}
```

Pedido de mudança: {pedido}

Instruções:
1. Faça APENAS a mudança pedida — não refatore ou "melhore" outras partes do código.
2. Depois do código, explique em 1-2 frases o que mudou e por quê.
3. Se o pedido for ambíguo em algum ponto, diga qual suposição você fez.
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


if __name__ == "__main__":
    resultado = pedir_mudanca_com_justificativa(codigo_atual, pedido)
    print(resultado)
    print("\n--- Lembrete ---")
    print("Revise o código gerado e a suposição feita ANTES de aplicar a mudança.")

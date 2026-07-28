"""Gera testes automatizados a partir de uma função existente e REALMENTE os
executa — a etapa de verificação da aula 7.3 não pode parar em "o modelo disse que
parece certo": rodar os testes de verdade é o que efetivamente confirma o comportamento."""
import subprocess
import tempfile
from pathlib import Path

import anthropic

client = anthropic.Anthropic()

codigo_fonte = '''\
def aplicar_desconto(preco: float, percentual_desconto: float) -> float:
    if not (0 <= percentual_desconto <= 100):
        raise ValueError("percentual_desconto deve estar entre 0 e 100")
    if preco < 0:
        raise ValueError("preco deve ser maior ou igual a 0")
    return round(preco * (1 - percentual_desconto / 100), 2)
'''


def gerar_testes(codigo: str) -> str:
    prompt = f"""\
Escreva testes usando pytest para a função abaixo. Cubra: caso normal, valores limite
(0% e 100% de desconto), e os dois casos de erro (percentual e preço inválidos).

```python
{codigo}
```

Responda APENAS com o código dos testes (incluindo o import da função como
`from funcao import aplicar_desconto`), sem explicação.
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = r.content[0].text
    # Remove markdown fences se o modelo os incluir, mesmo pedindo só o código.
    return texto.replace("```python", "").replace("```", "").strip()


def rodar_testes_gerados(codigo_fonte: str, codigo_testes: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        (pasta / "funcao.py").write_text(codigo_fonte, encoding="utf-8")
        (pasta / "test_funcao.py").write_text(codigo_testes, encoding="utf-8")

        resultado = subprocess.run(
            ["python", "-m", "pytest", "-v", str(pasta / "test_funcao.py")],
            capture_output=True,
            text=True,
            cwd=pasta,
        )
        print(resultado.stdout)
        if resultado.returncode != 0:
            print("--- Testes falharam — revisar antes de aceitar a implementação ---")
            print(resultado.stderr)


if __name__ == "__main__":
    testes = gerar_testes(codigo_fonte)
    print("--- Testes gerados ---")
    print(testes)
    print("\n--- Rodando os testes de verdade (pip install pytest) ---")
    rodar_testes_gerados(codigo_fonte, testes)

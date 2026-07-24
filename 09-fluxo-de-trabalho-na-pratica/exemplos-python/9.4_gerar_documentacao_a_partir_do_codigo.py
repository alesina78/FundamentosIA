"""Gera docstrings e um trecho de README a partir do código-fonte real — a
documentação nasce do código (fonte da verdade), reduzindo o risco de documentação
desatualizada em relação ao comportamento real da função."""
import anthropic

client = anthropic.Anthropic()

codigo_sem_docs = '''\
def aplicar_desconto(preco: float, percentual_desconto: float) -> float:
    if not (0 <= percentual_desconto <= 100):
        raise ValueError("percentual_desconto deve estar entre 0 e 100")
    if preco < 0:
        raise ValueError("preco deve ser maior ou igual a 0")
    return round(preco * (1 - percentual_desconto / 100), 2)
'''


def gerar_docstring(codigo: str) -> str:
    prompt = f"""\
Adicione uma docstring no formato Google Style à função abaixo, documentando
parâmetros, retorno e exceções levantadas. Não mude a lógica do código, apenas
adicione a docstring.

```python
{codigo}
```

Responda apenas com o código completo (função + docstring), sem explicação adicional.
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text.replace("```python", "").replace("```", "").strip()


def gerar_trecho_readme(codigo_com_docs: str) -> str:
    prompt = f"""\
Com base na função documentada abaixo, escreva um trecho de README em Markdown
explicando o que ela faz, com um exemplo de uso. Seja conciso — no máximo 10 linhas.

```python
{codigo_com_docs}
```
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


if __name__ == "__main__":
    codigo_documentado = gerar_docstring(codigo_sem_docs)
    print("--- Código com docstring ---")
    print(codigo_documentado)

    trecho_readme = gerar_trecho_readme(codigo_documentado)
    print("\n--- Trecho de README ---")
    print(trecho_readme)

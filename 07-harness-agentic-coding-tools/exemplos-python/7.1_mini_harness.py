"""
Um "mini harness" didático: um loop agentic (aula 4.2) com ferramentas de arquivo
reais (ler e escrever) — a versão simplificada do que um harness de agentic coding
como Claude Code faz por trás dos panos, mas sem hooks, permissions granulares,
subagents ou skills (aula 7.2 e 7.3 cobrem essas peças que faltam aqui).

ATENÇÃO: este script executa escrita de arquivos de verdade no diretório indicado
por PASTA_DE_TRABALHO. Rode em uma pasta de teste/descartável.
"""
import json
import os

import anthropic

client = anthropic.Anthropic()

PASTA_DE_TRABALHO = "./sandbox_mini_harness"
os.makedirs(PASTA_DE_TRABALHO, exist_ok=True)

tools = [
    {
        "name": "ler_arquivo",
        "description": "Lê o conteúdo de um arquivo dentro da pasta de trabalho.",
        "input_schema": {
            "type": "object",
            "properties": {"nome_arquivo": {"type": "string"}},
            "required": ["nome_arquivo"],
        },
    },
    {
        "name": "escrever_arquivo",
        "description": "Cria ou sobrescreve um arquivo dentro da pasta de trabalho.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nome_arquivo": {"type": "string"},
                "conteudo": {"type": "string"},
            },
            "required": ["nome_arquivo", "conteudo"],
        },
    },
]


def caminho_seguro(nome_arquivo: str) -> str:
    """Confina toda operação de arquivo à pasta de trabalho — nunca confie
    diretamente num path vindo do modelo (ver aula 7.3, sobre segurança)."""
    caminho = os.path.abspath(os.path.join(PASTA_DE_TRABALHO, nome_arquivo))
    raiz = os.path.abspath(PASTA_DE_TRABALHO)
    if not caminho.startswith(raiz):
        raise ValueError(f"Tentativa de acessar caminho fora da pasta de trabalho: {nome_arquivo}")
    return caminho


def executar_ferramenta(nome: str, entrada: dict) -> str:
    try:
        if nome == "ler_arquivo":
            caminho = caminho_seguro(entrada["nome_arquivo"])
            if not os.path.exists(caminho):
                return json.dumps({"erro": "arquivo não encontrado"})
            with open(caminho, encoding="utf-8") as f:
                return json.dumps({"conteudo": f.read()})
        if nome == "escrever_arquivo":
            caminho = caminho_seguro(entrada["nome_arquivo"])
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(entrada["conteudo"])
            return json.dumps({"status": "arquivo escrito com sucesso"})
        return json.dumps({"erro": f"ferramenta desconhecida: {nome}"})
    except ValueError as e:
        return json.dumps({"erro": str(e)})


def rodar_mini_harness(tarefa: str, max_iteracoes: int = 8) -> str:
    messages = [{"role": "user", "content": tarefa}]

    for _ in range(max_iteracoes):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=800,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                resultado = executar_ferramenta(block.name, block.input)
                print(f"  [{block.name}] {block.input} -> {resultado}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": resultado,
                })
        messages.append({"role": "user", "content": tool_results})

    return "Limite de iterações atingido."


if __name__ == "__main__":
    tarefa = (
        "Crie um arquivo chamado notas.txt com uma lista de 3 boas práticas de "
        "prompt engineering. Depois, leia o arquivo de volta e confirme o conteúdo."
    )
    print(rodar_mini_harness(tarefa))

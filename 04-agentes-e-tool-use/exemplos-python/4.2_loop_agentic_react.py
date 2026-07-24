import json

import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "somar",
        "description": "Soma dois números.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
    {
        "name": "multiplicar",
        "description": "Multiplica dois números.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
]


def executar_ferramenta(nome: str, entrada: dict) -> str:
    if nome == "somar":
        return json.dumps({"resultado": entrada["a"] + entrada["b"]})
    if nome == "multiplicar":
        return json.dumps({"resultado": entrada["a"] * entrada["b"]})
    return json.dumps({"erro": f"ferramenta desconhecida: {nome}"})


def resolver_com_loop_agentic(pergunta: str, max_iteracoes: int = 5) -> str:
    """Loop agentic: o modelo pode encadear várias chamadas de ferramenta até ter
    informação suficiente para responder. Padrão conhecido como ReAct
    (Reasoning + Acting): o modelo raciocina, age (chama ferramenta), observa o
    resultado, e decide se precisa agir de novo ou já pode responder."""
    messages = [{"role": "user", "content": pergunta}]

    for _ in range(max_iteracoes):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            tools=tools,
            messages=messages,
        )

        # Sem mais chamadas de ferramenta pendentes: o modelo já tem a resposta final.
        if response.stop_reason != "tool_use":
            return next(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})

        # Um turno pode conter várias chamadas de ferramenta em paralelo — trate todas.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                resultado = executar_ferramenta(block.name, block.input)
                print(f"  [ferramenta] {block.name}({block.input}) -> {resultado}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": resultado,
                })
        messages.append({"role": "user", "content": tool_results})

    return "Não foi possível resolver dentro do limite de iterações."


if __name__ == "__main__":
    # Requer duas chamadas de ferramenta em sequência: primeiro somar, depois multiplicar
    # pelo resultado — o modelo precisa encadear as chamadas sozinho.
    pergunta = "Some 4 com 6, depois multiplique o resultado por 3. Qual o valor final?"
    print(resolver_com_loop_agentic(pergunta))

import json

import anthropic

client = anthropic.Anthropic()

# 1. Defina a ferramenta: nome, descrição (crucial — o modelo decide QUANDO chamar com
# base nela) e o schema JSON dos parâmetros esperados.
tools = [
    {
        "name": "consultar_temperatura",
        "description": (
            "Retorna a temperatura atual de uma cidade. Chame esta ferramenta sempre que "
            "o usuário perguntar sobre o clima ou temperatura de um lugar específico."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cidade": {"type": "string", "description": "Nome da cidade, ex: 'São Paulo'"},
            },
            "required": ["cidade"],
        },
    }
]


def consultar_temperatura(cidade: str) -> str:
    """Implementação fake — numa aplicação real, chamaria uma API de clima de verdade."""
    temperaturas_fake = {"são paulo": 22, "rio de janeiro": 28, "curitiba": 15}
    temp = temperaturas_fake.get(cidade.lower(), 20)
    return json.dumps({"cidade": cidade, "temperatura_celsius": temp})


# 2. Primeira chamada: o modelo decide se precisa da ferramenta.
messages = [{"role": "user", "content": "Qual a temperatura em Curitiba agora?"}]

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    tools=tools,
    messages=messages,
)

print("stop_reason:", response.stop_reason)  # "tool_use" se decidiu chamar a ferramenta

# 3. Se o modelo pediu para usar a ferramenta, execute e devolva o resultado.
if response.stop_reason == "tool_use":
    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    resultado = consultar_temperatura(**tool_use_block.input)

    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": resultado,
        }],
    })

    # 4. Segunda chamada: agora o modelo tem o resultado e formula a resposta final.
    resposta_final = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        tools=tools,
        messages=messages,
    )
    print(resposta_final.content[0].text)

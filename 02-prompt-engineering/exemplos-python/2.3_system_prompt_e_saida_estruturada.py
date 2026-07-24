import json

import anthropic

client = anthropic.Anthropic()


# --- System prompt: define o "papel" e as regras gerais do modelo ---
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    system=(
        "Você é um assistente de suporte técnico para um provedor de internet residencial. "
        "Responda sempre em português, em no máximo 3 frases, e nunca prometa prazos "
        "que o cliente não informou."
    ),
    messages=[{"role": "user", "content": "Minha internet está lenta, o que eu faço?"}],
)
print("--- Com system prompt ---")
print(response.content[0].text)


# --- Formatação de saída: forçando um schema JSON válido ---
response_json = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": "Extraia os dados: 'João Silva, joao@email.com, quer o plano Enterprise.'",
    }],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "email": {"type": "string"},
                    "plano": {"type": "string"},
                },
                "required": ["nome", "email", "plano"],
                "additionalProperties": False,
            },
        }
    },
)
texto = next(b.text for b in response_json.content if b.type == "text")
dados = json.loads(texto)
print("\n--- Saída estruturada (JSON garantido) ---")
print(dados)

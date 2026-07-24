import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Explique em uma frase o que é um LLM."}
    ],
)

print(response.content[0].text)

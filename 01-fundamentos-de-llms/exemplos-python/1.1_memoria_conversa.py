import anthropic

client = anthropic.Anthropic()

messages = [{"role": "user", "content": "Meu nome é Ana."}]
r1 = client.messages.create(model="claude-haiku-4-5", max_tokens=50, messages=messages)
messages.append({"role": "assistant", "content": r1.content[0].text})

messages.append({"role": "user", "content": "Qual é o meu nome?"})
r2 = client.messages.create(model="claude-haiku-4-5", max_tokens=50, messages=messages)
print(r2.content[0].text)  # só funciona porque reenviamos o histórico

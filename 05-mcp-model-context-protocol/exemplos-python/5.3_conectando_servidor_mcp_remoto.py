"""
Conectando a API do Claude diretamente a um servidor MCP remoto, via o MCP connector
(beta) — a Anthropic faz a conexão com o servidor MCP no lado do servidor, sem você
precisar rodar um client MCP separado no seu código.
"""
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-haiku-4-5",
    max_tokens=500,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://exemplo-servidor-mcp.com/sse",
            "name": "servidor-de-pedidos",
            # "authorization_token": "...",  # se o servidor exigir autenticação
        }
    ],
    tools=[
        {"type": "mcp_toolset", "mcp_server_name": "servidor-de-pedidos"},
    ],
    messages=[{"role": "user", "content": "Qual o status do pedido 1001?"}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)

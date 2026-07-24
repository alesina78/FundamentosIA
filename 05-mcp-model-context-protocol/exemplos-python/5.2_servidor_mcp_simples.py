"""
Servidor MCP mínimo usando o SDK oficial Python (FastMCP).

pip install "mcp[cli]"

Para rodar e testar interativamente:
    mcp dev 5.2_servidor_mcp_simples.py

Para conectar como um servidor MCP "de verdade" a um client (Claude Desktop, Claude
Code, etc.), configure o client apontando para este arquivo via stdio.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Servidor de Pedidos")

# Base de dados fake — numa aplicação real, isso consultaria um banco de dados de verdade.
PEDIDOS = {
    "1001": {"status": "enviado", "previsao_entrega": "2026-07-28"},
    "1002": {"status": "processando", "previsao_entrega": "2026-08-02"},
}


@mcp.tool()
def consultar_status_pedido(numero_pedido: str) -> dict:
    """Consulta o status de um pedido pelo número.

    Args:
        numero_pedido: o número identificador do pedido, ex: "1001".
    """
    pedido = PEDIDOS.get(numero_pedido)
    if pedido is None:
        return {"erro": f"Pedido {numero_pedido} não encontrado."}
    return pedido


@mcp.resource("pedidos://lista")
def listar_todos_pedidos() -> str:
    """Recurso somente-leitura: lista todos os pedidos cadastrados."""
    linhas = [f"{num}: {info['status']}" for num, info in PEDIDOS.items()]
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()

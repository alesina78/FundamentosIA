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
    "1001": {
        "cliente": "Ana Ribeiro",
        "status": "entregue",
        "previsao_entrega": "2026-07-28",
        "valor_total": 249.90,
    },
    "1002": {
        "cliente": "Bruno Tavares",
        "status": "processando",
        "previsao_entrega": "2026-08-12",
        "valor_total": 89.00,
    },
    "1003": {
        "cliente": "Carla Mendes",
        "status": "enviado",
        "previsao_entrega": "2026-08-09",
        "valor_total": 1340.50,
    },
    "1004": {
        "cliente": "Diego Sampaio",
        "status": "aguardando pagamento",
        "previsao_entrega": None,
        "valor_total": 76.30,
    },
    "1005": {
        "cliente": "Ana Ribeiro",
        "status": "cancelado",
        "previsao_entrega": None,
        "valor_total": 512.00,
    },
    "1006": {
        "cliente": "Eduardo Lima",
        "status": "enviado",
        "previsao_entrega": "2026-08-07",
        "valor_total": 34.99,
    },
    "1007": {
        "cliente": "Fernanda Rocha",
        "status": "processando",
        "previsao_entrega": "2026-08-15",
        "valor_total": 2870.00,
    },
    "1008": {
        "cliente": "Gustavo Pinto",
        "status": "entregue",
        "previsao_entrega": "2026-06-30",
        "valor_total": 158.40,
    },
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
    linhas = [
        f"{num}: {info['cliente']} — {info['status']} — R$ {info['valor_total']:.2f}"
        for num, info in PEDIDOS.items()
    ]
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()

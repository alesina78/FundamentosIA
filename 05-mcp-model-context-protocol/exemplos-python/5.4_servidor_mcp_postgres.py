"""
Servidor MCP conectado a um banco Postgres real (hospedado no Render).

pip install "mcp[cli]" "psycopg[binary]" python-dotenv

Crie um arquivo .env ao lado deste, com a "External Database URL" que o Render mostra
na página do banco:

    DATABASE_URL=postgresql://usuario:senha@dpg-xxxx.oregon-postgres.render.com/meubanco

Para testar interativamente:
    mcp dev 5.4_servidor_mcp_postgres.py
"""
import os

import psycopg
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

mcp = FastMCP("Catálogo de Cursos")


def _conectar():
    # sslmode=require: o Render só aceita conexões TLS vindas de fora da rede dele.
    return psycopg.connect(DATABASE_URL, sslmode="require", row_factory=dict_row)


@mcp.tool()
def listar_cursos() -> list[dict]:
    """Lista todos os cursos do catálogo."""
    with _conectar() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, titulo, area, carga_horaria FROM cursos ORDER BY titulo")
        return cur.fetchall()


@mcp.tool()
def buscar_cursos_por_area(area: str) -> list[dict]:
    """Busca os cursos de uma área específica.

    Args:
        area: nome da área, ex: "IA", "Dados", "Backend".
    """
    with _conectar() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, titulo, area, carga_horaria FROM cursos WHERE area ILIKE %s",
            (area,),
        )
        return cur.fetchall()


if __name__ == "__main__":
    mcp.run()

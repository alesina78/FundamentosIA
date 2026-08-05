"""
Servidor MCP conectado a um banco Postgres real (hospedado no Render).

pip install "mcp[cli]" "psycopg[binary]" python-dotenv

Configure a variável de ambiente DATABASE_URL com a "External Database URL" que o
Render fornece na página do banco, por exemplo (num arquivo .env):

    DATABASE_URL=postgresql://usuario:senha@dpg-xxxx.oregon-postgres.render.com/meubanco

Para testar interativamente:
    mcp dev 5.4_servidor_mcp_postgres.py

Para conectar como servidor MCP no Claude Code:
    claude mcp add cursos -- python /caminho/absoluto/5.4_servidor_mcp_postgres.py
"""
import os
import re

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
def listar_cursos(area: str | None = None) -> list[dict]:
    """Lista os cursos do catálogo, opcionalmente filtrando por área.

    Args:
        area: área do curso, ex: "IA", "Dados", "Backend". Omita para trazer todos.
    """
    sql = "SELECT id, titulo, area, carga_horaria, ativo FROM cursos"
    params: tuple = ()
    if area:
        sql += " WHERE area ILIKE %s"
        params = (area,)
    sql += " ORDER BY titulo"

    with _conectar() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


@mcp.tool()
def matriculas_do_curso(curso_id: int) -> list[dict]:
    """Lista os alunos matriculados em um curso.

    Args:
        curso_id: identificador numérico do curso (veja `listar_cursos`).
    """
    with _conectar() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.nome, a.email, m.data_matricula, m.concluido
            FROM matriculas m
            JOIN alunos a ON a.id = m.aluno_id
            WHERE m.curso_id = %s
            ORDER BY m.data_matricula
            """,
            (curso_id,),
        )
        return cur.fetchall()


# Padrões que denunciam uma query que não é apenas leitura.
_PROIBIDO = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|copy)\b", re.IGNORECASE
)


@mcp.tool()
def consulta_sql(query: str) -> list[dict]:
    """Executa uma consulta SELECT somente-leitura no banco e devolve as linhas.

    Args:
        query: uma única instrução SELECT. Escritas e DDL são rejeitadas.
    """
    q = query.strip().rstrip(";")
    if not q.lower().startswith("select"):
        return [{"erro": "Apenas instruções SELECT são permitidas."}]
    if ";" in q or _PROIBIDO.search(q):
        return [{"erro": "Query rejeitada: comando de escrita ou múltiplas instruções."}]

    with _conectar() as conn, conn.cursor() as cur:
        # Segunda barreira: mesmo que a checagem textual falhe, a transação é read-only.
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute(f"SELECT * FROM ({q}) AS sub LIMIT 100")
        return cur.fetchall()


@mcp.resource("banco://schema")
def schema_do_banco() -> str:
    """Recurso somente-leitura: tabelas e colunas disponíveis no schema public."""
    with _conectar() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        )
        linhas = cur.fetchall()

    return "\n".join(
        f"{l['table_name']}.{l['column_name']}: {l['data_type']}" for l in linhas
    )


if __name__ == "__main__":
    mcp.run()

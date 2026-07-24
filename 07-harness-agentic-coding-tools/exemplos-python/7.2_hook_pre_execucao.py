"""Demonstra o CONCEITO de hook: um ponto de extensão que roda ANTES de uma
ferramenta ser executada, podendo bloquear, logar ou modificar a chamada. Isso é
uma versão simplificada e didática — o Claude Code implementa hooks de forma nativa
via configuração (settings.json), sem precisar escrever esse código na mão."""
import json
from datetime import datetime

LOG_PATH = "hook_execucoes.log"

# Padrão de arquivo que o hook nunca deixa escrever, não importa o que o modelo peça.
ARQUIVOS_PROTEGIDOS = {".env", "credentials.json", "id_rsa"}


def hook_pre_tool_use(nome_ferramenta: str, entrada: dict) -> tuple[bool, str | None]:
    """Roda antes de qualquer ferramenta ser executada.
    Retorna (permitido, motivo_do_bloqueio)."""

    # 1. Log de auditoria — toda chamada de ferramenta fica registrada.
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {nome_ferramenta} | {json.dumps(entrada)}\n")

    # 2. Bloqueio automático de arquivos sensíveis, independente do que o modelo decidiu.
    if nome_ferramenta == "escrever_arquivo":
        nome_arquivo = entrada.get("nome_arquivo", "")
        if any(protegido in nome_arquivo for protegido in ARQUIVOS_PROTEGIDOS):
            return False, f"Bloqueado por hook: '{nome_arquivo}' é um arquivo protegido."

    return True, None


if __name__ == "__main__":
    # Simulação: duas chamadas de ferramenta, uma legítima e uma bloqueada pelo hook.
    chamadas = [
        ("escrever_arquivo", {"nome_arquivo": "notas.txt", "conteudo": "..."}),
        ("escrever_arquivo", {"nome_arquivo": ".env", "conteudo": "API_KEY=secreta"}),
    ]

    for nome, entrada in chamadas:
        permitido, motivo = hook_pre_tool_use(nome, entrada)
        if permitido:
            print(f"[OK] {nome}({entrada}) — executaria normalmente")
        else:
            print(f"[BLOQUEADO] {nome}({entrada}) — {motivo}")

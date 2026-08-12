"""Hook real do Claude Code: no evento `Stop` (fim do turno do agente), grava uma
nota diária de memória num vault do Obsidian.

Registre em ~/.claude/settings.json:

    {"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": "python ~/.claude/hooks/memoria_obsidian.py"}
    ]}]}}

Teste isolado, sem o harness:

    echo '{"session_id":"abc123","cwd":"/meu/projeto"}' | python 6.2_hook_memoria_obsidian.py
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajuste para o seu vault. A pasta é criada se não existir.
VAULT = Path(os.environ.get("OBSIDIAN_VAULT", Path.home() / "Obsidian" / "Vault"))
PASTA_MEMORIA = VAULT / "Memoria IA"


def ler_evento() -> dict:
    """O harness entrega o payload do evento pelo stdin, em JSON."""
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def ultima_mensagem(transcript_path: str | None) -> str:
    """Extrai a última resposta do assistente do transcript (JSONL) da sessão."""
    if not transcript_path or not Path(transcript_path).exists():
        return "(sem transcript disponível)"

    ultima = ""
    with open(transcript_path, encoding="utf-8") as f:
        for linha in f:
            try:
                registro = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if registro.get("type") != "assistant":
                continue
            for bloco in registro.get("message", {}).get("content", []):
                if bloco.get("type") == "text":
                    ultima = bloco["text"]
    return ultima.strip() or "(sem texto)"


def escrever_nota(evento: dict) -> None:
    hoje = datetime.now()
    nota = PASTA_MEMORIA / f"{hoje:%Y-%m-%d}.md"
    projeto = Path(evento.get("cwd", os.getcwd())).name

    PASTA_MEMORIA.mkdir(parents=True, exist_ok=True)
    if not nota.exists():
        # Frontmatter só na criação; os turnos seguintes do dia são anexados.
        nota.write_text(
            f"---\ntipo: memoria-ia\ndata: {hoje:%Y-%m-%d}\n---\n\n"
            f"# Sessões com IA — {hoje:%d/%m/%Y}\n",
            encoding="utf-8",
        )

    with open(nota, "a", encoding="utf-8") as f:
        # O link [[projeto]] conecta a nota ao resto do vault — é o que torna
        # essa memória navegável e pesquisável depois.
        f.write(
            f"\n## {hoje:%H:%M} — [[{projeto}]]\n"
            f"- Sessão: `{evento.get('session_id', 'desconhecida')}`\n\n"
            f"{ultima_mensagem(evento.get('transcript_path'))}\n"
        )


if __name__ == "__main__":
    try:
        escrever_nota(ler_evento())
    except Exception as erro:
        # Falha do hook nunca deve travar o fluxo de trabalho: avisa no stderr
        # e sai com 0, que o harness interpreta como "siga em frente".
        print(f"[hook memoria] falhou: {erro}", file=sys.stderr)
    sys.exit(0)

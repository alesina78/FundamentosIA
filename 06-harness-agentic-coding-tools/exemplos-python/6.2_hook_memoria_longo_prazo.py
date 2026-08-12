"""Hook real do Claude Code: no evento `Stop` — quando o agente termina o turno e a
sessao fica ociosa — grava uma nota curta em Markdown numa pasta local, formando a
memoria de longo prazo do agente.

Registre em ~/.claude/settings.json:

    {"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": "python ~/.claude/hooks/memoria.py"}
    ]}]}}

Teste isolado, sem o harness:

    echo '{"session_id":"abc123","cwd":"/meu/projeto"}' | python 6.2_hook_memoria_longo_prazo.py
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Pasta da memoria. Simples arquivos .md no disco — sem app nenhum por cima.
PASTA_MEMORIA = Path(os.environ.get("MEMORIA_IA", Path.home() / ".claude" / "memoria"))

# Notas longas nao sao memoria, sao transcript. Cortamos duro de proposito.
MAX_FRASES = 2
MAX_CARACTERES = 240


def ler_evento() -> dict:
    """O harness entrega o payload do evento pelo stdin, em JSON."""
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def ultima_resposta(transcript_path: str | None) -> str:
    """Extrai a ultima resposta do assistente do transcript (JSONL) da sessao."""
    if not transcript_path or not Path(transcript_path).exists():
        return ""

    texto = ""
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
                    texto = bloco["text"]
    return texto


def resumir(texto: str) -> str:
    """Reduz a resposta a uma nota curta e objetiva: sem blocos de codigo, sem
    listas, sem markdown — so as primeiras frases em prosa."""
    if not texto.strip():
        return "(sem resposta registrada)"

    texto = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)  # fora blocos de codigo
    texto = re.sub(r"^\s*[-*#>|].*$", "", texto, flags=re.MULTILINE)  # fora listas/titulos
    texto = re.sub(r"\s+", " ", texto).strip()

    if not texto:
        return "(sem resposta em prosa)"

    frases = re.split(r"(?<=[.!?])\s+", texto)[:MAX_FRASES]
    nota = " ".join(frases)
    return nota[:MAX_CARACTERES].rstrip() + ("…" if len(nota) > MAX_CARACTERES else "")


def escrever_nota(evento: dict) -> None:
    agora = datetime.now()
    projeto = Path(evento.get("cwd", os.getcwd())).name

    # Uma pasta por projeto, um arquivo por dia: a memoria fica navegavel a olho
    # nu e facil de recuperar depois (por grep ou por RAG).
    destino = PASTA_MEMORIA / projeto
    destino.mkdir(parents=True, exist_ok=True)
    nota = destino / f"{agora:%Y-%m-%d}.md"

    if not nota.exists():
        nota.write_text(
            f"---\ntipo: memoria-ia\nprojeto: {projeto}\ndata: {agora:%Y-%m-%d}\n---\n",
            encoding="utf-8",
        )

    with open(nota, "a", encoding="utf-8") as f:
        f.write(f"\n- **{agora:%H:%M}** — {resumir(ultima_resposta(evento.get('transcript_path')))}\n")


if __name__ == "__main__":
    try:
        escrever_nota(ler_evento())
    except Exception as erro:
        # Falha do hook nunca deve travar o fluxo de trabalho: avisa no stderr
        # e sai com 0, que o harness interpreta como "siga em frente".
        print(f"[hook memoria] falhou: {erro}", file=sys.stderr)
    sys.exit(0)

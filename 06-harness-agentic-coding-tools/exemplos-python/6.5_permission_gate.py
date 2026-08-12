"""Demonstra o CONCEITO de um sistema de permissions: classificar cada chamada de
ferramenta em "permitir automaticamente", "pedir confirmação" ou "sempre negar",
com base no risco da ação — o mesmo princípio usado por harnesses reais como o
Claude Code (lá, configurado declarativamente; aqui, ilustrado em código)."""
from enum import Enum


class Decisao(Enum):
    PERMITIR = "permitir"
    PEDIR_CONFIRMACAO = "pedir_confirmacao"
    NEGAR = "negar"


# Regras de permissão — ações somente-leitura são automáticas; ações que modificam
# ou têm efeito externo pedem confirmação; ações destrutivas são sempre negadas.
REGRAS = {
    "ler_arquivo": Decisao.PERMITIR,
    "buscar_no_codigo": Decisao.PERMITIR,
    "escrever_arquivo": Decisao.PEDIR_CONFIRMACAO,
    "rodar_comando_terminal": Decisao.PEDIR_CONFIRMACAO,
    "enviar_email": Decisao.PEDIR_CONFIRMACAO,
    "deletar_arquivo": Decisao.NEGAR,
    "forcar_push_git": Decisao.NEGAR,
}


def avaliar_permissao(nome_ferramenta: str) -> Decisao:
    """Retorna a decisão padrão para uma ferramenta. Ferramentas não listadas são
    tratadas como alto risco por padrão (negar), nunca como permitidas por padrão —
    ver "Pontos-Chave" na aula sobre por que esse é o padrão seguro."""
    return REGRAS.get(nome_ferramenta, Decisao.NEGAR)


def executar_com_gate(nome_ferramenta: str, entrada: dict, confirmar_com_usuario) -> str:
    """confirmar_com_usuario: função que pergunta ao humano e retorna True/False —
    numa aplicação real, seria um prompt no terminal ou uma UI."""
    decisao = avaliar_permissao(nome_ferramenta)

    if decisao == Decisao.NEGAR:
        return f"[NEGADO] '{nome_ferramenta}' não é permitido automaticamente."

    if decisao == Decisao.PEDIR_CONFIRMACAO:
        if not confirmar_com_usuario(nome_ferramenta, entrada):
            return f"[CANCELADO PELO USUÁRIO] '{nome_ferramenta}' com {entrada}"

    return f"[EXECUTADO] '{nome_ferramenta}' com {entrada}"


if __name__ == "__main__":
    def confirmar_automaticamente(nome, entrada):
        # Simula um usuário aprovando tudo — numa aplicação real, seria input() real.
        print(f"  (pedindo confirmação para {nome}({entrada})... aprovado)")
        return True

    print(executar_com_gate("ler_arquivo", {"nome_arquivo": "README.md"}, confirmar_automaticamente))
    print(executar_com_gate("escrever_arquivo", {"nome_arquivo": "notas.txt"}, confirmar_automaticamente))
    print(executar_com_gate("deletar_arquivo", {"nome_arquivo": "producao.db"}, confirmar_automaticamente))
    print(executar_com_gate("ferramenta_desconhecida", {}, confirmar_automaticamente))

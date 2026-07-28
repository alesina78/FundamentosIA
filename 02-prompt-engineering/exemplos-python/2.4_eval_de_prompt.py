"""
Eval determinístico de prompt: mesmo dataset, dois prompts, taxa de acerto lado a lado.

A tarefa é classificação de mensagens de suporte em categorias fechadas — escolhida de
propósito porque o acerto é verificável por comparação exata (`==`), sem precisar de
julgamento humano nem de um segundo modelo como juiz.

Repare que o dataset abaixo é FIXO: é ele que permite dizer que o prompt B é melhor que o
prompt A. Se você mudar o prompt e o dataset ao mesmo tempo, os números deixam de ser
comparáveis.
"""
import anthropic

client = anthropic.Anthropic()

CATEGORIAS = ["cobranca", "tecnico", "cancelamento", "elogio"]

# Dataset de avaliação: (mensagem, categoria esperada).
# Inclui casos fáceis e casos de borda de propósito — um dataset só com casos óbvios
# dá 100% em qualquer prompt e não serve para comparar nada.
DATASET = [
    ("Minha fatura veio com valor errado esse mês", "cobranca"),
    ("A internet cai toda noite por volta das 22h", "tecnico"),
    ("Quero encerrar meu contrato", "cancelamento"),
    ("O técnico que veio aqui foi excelente, parabéns", "elogio"),
    # Casos de borda: dois assuntos na mesma mensagem, ou intenção implícita.
    ("Estou pagando caro e a conexão vive lenta, quero encerrar", "cancelamento"),
    ("Fui cobrado duas vezes, o suporte resolveu rápido e bem", "cobranca"),
    ("Não consigo acessar a segunda via no aplicativo", "tecnico"),
    ("Vocês debitaram antes do vencimento de novo", "cobranca"),
    ("Pensei em sair mas o atendimento me convenceu a ficar", "elogio"),
    ("Meu roteador pisca vermelho desde a troca de plano", "tecnico"),
]

# Prompt A: instrução vaga, sem definir as categorias nem restringir o formato da saída.
PROMPT_A = """\
Classifique a mensagem de suporte abaixo em uma categoria.

Mensagem: {mensagem}
"""

# Prompt B: categorias explícitas, regra de desempate para os casos de borda e formato de
# saída restrito a uma única palavra — as três coisas que o prompt A deixou em aberto.
PROMPT_B = """\
Classifique a mensagem de suporte abaixo em exatamente uma destas categorias:
cobranca, tecnico, cancelamento, elogio

Regra de desempate: se a mensagem tratar de mais de um assunto, classifique pela intenção
principal do cliente — o que ele quer que aconteça a seguir.

Responda APENAS com o nome da categoria, em minúsculas, sem pontuação e sem explicação.

Mensagem: {mensagem}
"""


def classificar(template: str, mensagem: str) -> str:
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=20,
        # temperature=0 reduz a variação entre execuções: num eval, você quer que a
        # diferença observada venha do prompt, não da aleatoriedade da amostragem.
        temperature=0,
        messages=[{"role": "user", "content": template.format(mensagem=mensagem)}],
    )
    return r.content[0].text.strip().lower()


def rodar_eval(nome: str, template: str) -> float:
    """Roda o dataset inteiro contra um prompt e devolve a taxa de acerto."""
    acertos = 0
    print(f"\n--- Eval: {nome} ---")
    for mensagem, esperado in DATASET:
        obtido = classificar(template, mensagem)
        # Critério determinístico de acerto: comparação exata com o gabarito.
        ok = obtido == esperado
        acertos += ok
        if not ok:
            # Só os erros são impressos — é neles que está a informação para a
            # próxima iteração do prompt.
            print(f"  [ERRO] esperado={esperado!r} obtido={obtido!r} | {mensagem}")

    taxa = acertos / len(DATASET)
    print(f"  Acertos: {acertos}/{len(DATASET)} ({taxa:.0%})")
    return taxa


if __name__ == "__main__":
    taxa_a = rodar_eval("Prompt A (vago)", PROMPT_A)
    taxa_b = rodar_eval("Prompt B (categorias + desempate + formato)", PROMPT_B)

    print("\n--- Comparação ---")
    print(f"Prompt A: {taxa_a:.0%}")
    print(f"Prompt B: {taxa_b:.0%}")
    print(f"Diferença: {taxa_b - taxa_a:+.0%}")

    # Um eval também serve como teste de regressão: fixe um mínimo aceitável e falhe
    # quando uma mudança de prompt (ou de modelo) ficar abaixo dele.
    LIMIAR = 0.8
    if taxa_b < LIMIAR:
        print(f"\nATENÇÃO: prompt B abaixo do limiar de {LIMIAR:.0%} — revisar antes de usar.")

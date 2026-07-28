"""
Eval determinístico de prompt: mesmo dataset, dois prompts, taxa de acerto lado a lado.

A tarefa é classificação de mensagens de suporte em categorias fechadas — escolhida de
propósito porque o acerto é verificável automaticamente, sem precisar de julgamento humano
nem de um segundo modelo como juiz.

Duas métricas são reportadas por prompt, e a razão disso é a lição central do exercício:
um `==` cru contra o gabarito reprova junto o modelo que errou a categoria e o que acertou
mas respondeu em markdown — falhas com causas e correções diferentes.

Repare que o dataset abaixo é FIXO: é ele que permite dizer que o prompt B é melhor que o
prompt A. Se você mudar o prompt e o dataset ao mesmo tempo, os números deixam de ser
comparáveis.
"""
import unicodedata

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
        # Folga suficiente para o prompt A terminar a frase. Com max_tokens apertado, a
        # saída dele seria cortada no meio e o eval mediria truncamento, não qualidade.
        max_tokens=150,
        # temperature=0 reduz a variação entre execuções: num eval, você quer que a
        # diferença observada venha do prompt, não da aleatoriedade da amostragem.
        temperature=0,
        messages=[{"role": "user", "content": template.format(mensagem=mensagem)}],
    )
    return r.content[0].text.strip().lower()


def _normalizar(texto: str) -> str:
    """Remove acentos e caixa, para que 'Cobrança' case com 'cobranca'."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def extrair_categoria(saida: str) -> str | None:
    """Encontra a primeira categoria conhecida mencionada na saída, seja ela uma resposta
    limpa ('cobranca') ou verbosa ('# Classificação: **Cobrança/Faturamento**').
    Devolve None quando o modelo usou uma categoria que não existe no nosso conjunto."""
    normalizada = _normalizar(saida)
    posicoes = [(normalizada.find(c), c) for c in CATEGORIAS if c in normalizada]
    return min(posicoes)[1] if posicoes else None


def rodar_eval(nome: str, template: str) -> tuple[float, float]:
    """Roda o dataset contra um prompt e devolve duas taxas: formato e categoria.

    Medir as duas separadamente é o ponto do exercício. Um `==` cru contra o gabarito
    reprovaria por igual o modelo que errou a categoria e o que acertou mas respondeu em
    markdown — duas falhas com causas e correções completamente diferentes.
    """
    formato_ok = 0
    categoria_ok = 0
    print(f"\n--- Eval: {nome} ---")

    for mensagem, esperado in DATASET:
        saida = classificar(template, mensagem)

        # Métrica 1 — formato: a saída é exatamente o nome de uma categoria, e nada mais?
        # É o que o seu código precisa para usar a resposta sem pós-processamento.
        formato = saida in CATEGORIAS

        # Métrica 2 — acerto de categoria: a classificação está certa, mesmo que a saída
        # tenha vindo embrulhada em texto. É a capacidade do modelo na tarefa em si.
        obtido = extrair_categoria(saida)
        acertou = obtido == esperado

        formato_ok += formato
        categoria_ok += acertou

        if not acertou or not formato:
            # Só os casos com problema são impressos — é neles que está a informação
            # para a próxima iteração do prompt.
            motivo = "categoria errada" if not acertou else "formato fora do esperado"
            print(f"  [{motivo:<24}] esperado={esperado!r} saída={saida[:60]!r}")

    n = len(DATASET)
    print(f"  Formato válido:      {formato_ok}/{n} ({formato_ok / n:.0%})")
    print(f"  Categoria correta:   {categoria_ok}/{n} ({categoria_ok / n:.0%})")
    return formato_ok / n, categoria_ok / n


if __name__ == "__main__":
    formato_a, categoria_a = rodar_eval("Prompt A (vago)", PROMPT_A)
    formato_b, categoria_b = rodar_eval("Prompt B (categorias + desempate + formato)", PROMPT_B)

    print("\n--- Comparação ---")
    print(f"{'':<12} {'formato':>9} {'categoria':>11}")
    print(f"{'Prompt A':<12} {formato_a:>8.0%} {categoria_a:>10.0%}")
    print(f"{'Prompt B':<12} {formato_b:>8.0%} {categoria_b:>10.0%}")
    print(f"{'Diferença':<12} {formato_b - formato_a:>+8.0%} {categoria_b - categoria_a:>+10.0%}")

    print(
        "\nAs duas colunas contam histórias diferentes: sem listar as categorias, o prompt A\n"
        "inventa rótulos próprios ('acesso/login', 'reclamação') e responde em markdown.\n"
        "O ganho do prompt B vem de três coisas somadas — categorias explícitas, regra de\n"
        "desempate e formato restrito — e só o eval separado mostra o peso de cada uma."
    )

    # Um eval também serve como teste de regressão: fixe um mínimo aceitável e falhe
    # quando uma mudança de prompt (ou de modelo) ficar abaixo dele.
    LIMIAR = 0.8
    if categoria_b < LIMIAR:
        print(f"\nATENÇÃO: prompt B abaixo do limiar de {LIMIAR:.0%} — revisar antes de usar.")

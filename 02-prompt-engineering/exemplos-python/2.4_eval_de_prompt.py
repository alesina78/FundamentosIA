"""
Módulo de Avaliação Determinística de Prompts (Prompt Eval).

Este script realiza uma avaliação comparativa de desempenho entre dois prompts
distintos aplicados a um dataset fixo de mensagens de suporte. A tarefa consiste
em classificar o texto em categorias fechadas, permitindo mensurar de forma
determinística tanto a aderência ao formato de saída quanto a precisão semântica.

Conceitos-chave demonstrados:
    - Uso de dataset fixo e versionável para garantir comparabilidade.
    - Avaliação desacoplada: validação separada de formato vs. acerto de categoria.
    - Execução paralela controlada via ThreadPoolExecutor para otimizar chamadas de API.
    - Configuração determinística (temperature=0) para isolar variáveis de prompt.
"""

from concurrent.futures import ThreadPoolExecutor
import unicodedata
import anthropic

# Inicialização do cliente da API da Anthropic
client = anthropic.Anthropic()

# Definição das categorias aceitas pelo sistema
CATEGORIAS = ["cobranca", "tecnico", "cancelamento", "elogio"]

# Limite de requisições simultâneas (Threads) para evitar erros de Rate Limit (429)
MAX_WORKERS = 5

# Dataset de avaliação imutável contendo tuplas de (mensagem, categoria_esperada).
# Inclui intencionalmente casos simples e de borda (múltiplos assuntos ou intenção implícita).
DATASET = [
    ("Minha fatura veio com valor errado esse mês", "cobranca"),
    ("A internet cai toda noite por volta das 22h", "tecnico"),
    ("Quero encerrar meu contrato", "cancelamento"),
    ("O técnico que veio aqui foi excelente, parabéns", "elogio"),
    # Casos de borda: múltiplos assuntos ou intenções implícitas
    ("Estou pagando caro e a conexão vive lenta, quero encerrar", "cancelamento"),
    ("Fui cobrado duas vezes, o suporte resolveu rápido e bem", "cobranca"),
    ("Não consigo acessar a segunda via no aplicativo", "tecnico"),
    ("Vocês debitaram antes do vencimento de novo", "cobranca"),
    ("Pensei em sair mas o atendimento me convenceu a ficar", "elogio"),
    ("Meu roteador pisca vermelho desde a troca de plano", "tecnico"),
]

# Prompt A: Instrução vaga, sem definição de categorias e sem restrição de formato.
PROMPT_A = """\
Classifique a mensagem de suporte abaixo em uma categoria.

Mensagem: {mensagem}
"""

# Prompt B: Instruções restritivas, categorias explícitas e regras de desempate.
PROMPT_B = """\
Classifique a mensagem de suporte abaixo em exatamente uma destas categorias:
cobranca, tecnico, cancelamento, elogio

Regra de desempate: se a mensagem tratar de mais de um assunto, classifique pela intenção
principal do cliente — o que ele quer que aconteça a seguir.

Responda APENAS com o nome da categoria, em minúsculas, sem pontuação e sem explicação.

Mensagem: {mensagem}
"""


def classificar(template: str, mensagem: str) -> str:
    """Envia uma mensagem para o modelo Claude e retorna a resposta normalizada.

    Args:
        template (str): O template do prompt contendo a chave '{mensagem}'.
        mensagem (str): O texto de suporte a ser classificado.

    Returns:
        str: A resposta do modelo limpa (em minúsculas e sem espaços excedentes).
    """
    resposta = client.messages.create(
        model="claude-haiku-4-5",
        # max_tokens com folga para permitir que prompts vagos terminem a frase,
        # evitando avaliar truncamento por falha de limite de tokens.
        max_tokens=150,
        # temperature=0 garante determinismo, isolando variações ao próprio prompt.
        temperature=0,
        messages=[{"role": "user", "content": template.format(mensagem=mensagem)}],
    )
    return resposta.content[0].text.strip().lower()


def _normalizar(texto: str) -> str:
    """Remove acentos e converte o texto para minúsculas.

    Utilizado para garantir correspondência robusta (ex: 'Cobrança' vira 'cobranca').

    Args:
        texto (str): O texto bruto a ser normalizado.

    Returns:
        str: Texto sem acentos e em letras minúsculas.
    """
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def extrair_categoria(saida: str) -> str | None:
    """Extrai a primeira categoria válida encontrada na saída do modelo.

    Lida tanto com respostas limpas ('cobranca') quanto com respostas verbosas
    em Markdown (ex: '# Classificação: **Cobrança/Faturamento**').

    Args:
        saida (str): A string de resposta retornada pelo LLM.

    Returns:
        str | None: O nome da categoria identificada ou None se nenhuma for encontrada.
    """
    normalizada = _normalizar(saida)
    posicoes = [(normalizada.find(c), c) for c in CATEGORIAS if c in normalizada]
    return min(posicoes)[1] if posicoes else None


def rodar_eval(nome: str, template: str) -> tuple[float, float]:
    """Executa o dataset completo contra um prompt específico e calcula métricas.

    Args:
        nome (str): Rótulo descritivo do prompt testado (ex: 'Prompt A').
        template (str): O template de prompt a ser avaliado.

    Returns:
        tuple[float, float]: Uma tupla contendo a taxa de sucesso de formato
        e a taxa de acerto de categoria (valores entre 0.0 e 1.0).
    """
    formato_ok = 0
    categoria_ok = 0
    print(f"\n--- Avaliação (Eval): {nome} ---")

    # Executa as chamadas em paralelo para otimizar o tempo de rede.
    # O ThreadPoolExecutor preserva a ordem original via map().
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        saidas = list(executor.map(lambda caso: classificar(template, caso[0]), DATASET))

    for (mensagem, esperado), saida in zip(DATASET, saidas):
        # Métrica 1 (Formato): A resposta atende estritamente às restrições de formato?
        formato = saida in CATEGORIAS

        # Métrica 2 (Conteúdo): A categoria esperada está presente/correta na saída?
        obtido = extrair_categoria(saida)
        acertou = obtido == esperado

        formato_ok += int(formato)
        categoria_ok += int(acertou)

        # Log detalhado apenas para falhas (auxilia na iteração de engenharia de prompt)
        if not acertou or not formato:
            motivo = "Categoria errada" if not acertou else "Formato inválido"
            print(f"  [{motivo:<18}] Esperado={esperado!r} | Saída={saida[:50]!r}")
            print(f"  {'':<20} Mensagem: {mensagem}")

    total_casos = len(DATASET)
    taxa_formato = formato_ok / total_casos
    taxa_categoria = categoria_ok / total_casos

    print(f"  Aderência de Formato:  {formato_ok}/{total_casos} ({taxa_formato:.0%})")
    print(f"  Acurácia de Categoria: {categoria_ok}/{total_casos} ({taxa_categoria:.0%})")
    
    return taxa_formato, taxa_categoria


if __name__ == "__main__":
    # Executa a avaliação para ambos os cenários de prompt
    formato_a, categoria_a = rodar_eval("Prompt A (Vago)", PROMPT_A)
    formato_b, categoria_b = rodar_eval("Prompt B (Estruturado)", PROMPT_B)

    # Exibição do relatório comparativo consolidado
    print("\n--- Relatório Comparativo ---")
    print(f"{'Prompt':<24} {'Formato':>10} {'Categoria':>12}")
    print(f"{'Prompt A (Vago)':<24} {formato_a:>9.0%} {categoria_a:>11.0%}")
    print(f"{'Prompt B (Estruturado)':<24} {formato_b:>9.0%} {categoria_b:>11.0%}")
    print(f"{'Evolução (Delta)':<24} {formato_b - formato_a:>+9.0%} {categoria_b - categoria_a:>+11.0%}")

    print(
        "\nAnálise do Resultado:\n"
        "  - O Prompt A sofre com o desalinhamento de formato (responde em markdown/rótulos livres).\n"
        "  - O Prompt B isola e resolve o problema com restrições explícitas e regras de desempate,\n"
        "    demonstrando a importância de separar as métricas de estrutura e conteúdo no Eval."
    )

    # Teste de Regressão Automatizado
    LIMIAR_ACEITAVEL = 0.80
    if categoria_b < LIMIAR_ACEITAVEL:
        print(f"\n[ALERTA] Desempenho do Prompt B abaixo do limiar crítico de {LIMIAR_ACEITAVEL:.0%}!")
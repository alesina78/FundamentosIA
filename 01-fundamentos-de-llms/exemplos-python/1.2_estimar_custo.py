# Preços ilustrativos (sempre consulte a página oficial de pricing antes de usar em produção)
PRECO_INPUT_POR_MTOK = 3.00   # USD por milhão de tokens de entrada
PRECO_OUTPUT_POR_MTOK = 15.00  # USD por milhão de tokens de saída


def estimar_custo(tokens_input: int, tokens_output: int) -> float:
    custo_input = (tokens_input / 1_000_000) * PRECO_INPUT_POR_MTOK
    custo_output = (tokens_output / 1_000_000) * PRECO_OUTPUT_POR_MTOK
    return round(custo_input + custo_output, 6)


print(estimar_custo(tokens_input=1200, tokens_output=300))  # ex: 0.0081

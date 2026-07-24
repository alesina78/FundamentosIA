"""Duas estratégias simples de chunking para preparar documentos longos para RAG."""


def chunk_por_tamanho_fixo(texto: str, tamanho: int = 500, sobreposicao: int = 50) -> list[str]:
    """Divide o texto em pedaços de tamanho fixo (em caracteres), com sobreposição
    entre chunks para não perder contexto que ficaria cortado na fronteira."""
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += tamanho - sobreposicao
    return chunks


def chunk_por_paragrafo(texto: str, max_chars_por_chunk: int = 800) -> list[str]:
    """Divide respeitando os parágrafos originais — cada chunk agrupa parágrafos
    inteiros até atingir o limite de tamanho, evitando cortar no meio de uma ideia."""
    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    chunks = []
    chunk_atual = ""
    for paragrafo in paragrafos:
        if len(chunk_atual) + len(paragrafo) > max_chars_por_chunk and chunk_atual:
            chunks.append(chunk_atual.strip())
            chunk_atual = ""
        chunk_atual += paragrafo + "\n\n"
    if chunk_atual.strip():
        chunks.append(chunk_atual.strip())
    return chunks


if __name__ == "__main__":
    documento = """Política de Reembolso

Produtos podem ser devolvidos em até 30 dias após a compra, desde que estejam na
embalagem original e sem sinais de uso.

Horário de Atendimento

Nosso suporte funciona de segunda a sexta, das 9h às 18h, exceto feriados nacionais.

Frete

Frete grátis é aplicado automaticamente para compras acima de R$150 em todo o território
nacional, com prazo médio de 5 a 10 dias úteis."""

    print("--- Chunking por tamanho fixo ---")
    for i, chunk in enumerate(chunk_por_tamanho_fixo(documento, tamanho=150, sobreposicao=20)):
        print(f"[{i}] {chunk!r}")

    print("\n--- Chunking por parágrafo ---")
    for i, chunk in enumerate(chunk_por_paragrafo(documento, max_chars_por_chunk=200)):
        print(f"[{i}] {chunk!r}")

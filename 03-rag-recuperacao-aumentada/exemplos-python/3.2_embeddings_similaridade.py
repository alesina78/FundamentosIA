"""
A Anthropic não tem um endpoint próprio de embeddings — a parceira recomendada
oficialmente é a Voyage AI (voyageai.com), que tem free tier para começar.

pip install voyageai
"""
import math

import voyageai

vo = voyageai.Client()  # lê VOYAGE_API_KEY do ambiente

documentos = [
    "Política de reembolso: produtos podem ser devolvidos em até 30 dias após a compra.",
    "Horário de atendimento: suporte de segunda a sexta, das 9h às 18h.",
    "Frete grátis é aplicado automaticamente para compras acima de R$150.",
    "Trocas de tamanho em roupas são gratuitas dentro de 15 dias da entrega.",
]


def cosseno(a: list[float], b: list[float]) -> float:
    produto_escalar = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    return produto_escalar / (norma_a * norma_b)


def buscar_por_similaridade(pergunta: str, documentos: list[str], top_k: int = 2) -> list[str]:
    # Gera embeddings de todos os documentos de uma vez (mais eficiente que um a um).
    embeddings_docs = vo.embed(documentos, model="voyage-3.5", input_type="document").embeddings
    embedding_pergunta = vo.embed([pergunta], model="voyage-3.5", input_type="query").embeddings[0]

    pontuados = [
        (cosseno(embedding_pergunta, emb_doc), doc)
        for emb_doc, doc in zip(embeddings_docs, documentos)
    ]
    pontuados.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in pontuados[:top_k]]


if __name__ == "__main__":
    pergunta = "Posso trocar uma roupa que comprei há uma semana?"
    resultados = buscar_por_similaridade(pergunta, documentos)
    for doc in resultados:
        print("-", doc)

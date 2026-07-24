"""
RAG "manual" sem vector database — só para entender o conceito de retrieval + generation.
Numa aplicação real, a busca por palavra-chave abaixo seria substituída por busca
vetorial (aula 3.2), mas o fluxo geral (buscar -> montar contexto -> gerar) é o mesmo.
"""
import anthropic

client = anthropic.Anthropic()

# Nossa "base de conhecimento": documentos curtos e independentes.
documentos = [
    "Política de reembolso: produtos podem ser devolvidos em até 30 dias após a compra, "
    "desde que estejam na embalagem original.",
    "Horário de atendimento: nosso suporte funciona de segunda a sexta, das 9h às 18h.",
    "Frete grátis é aplicado automaticamente para compras acima de R$150.",
    "Trocas de tamanho em roupas são gratuitas dentro de 15 dias da entrega.",
]


def buscar_documentos_relevantes(pergunta: str, documentos: list[str], top_k: int = 2) -> list[str]:
    """Busca ingênua por sobreposição de palavras — só para fins didáticos.
    Em produção, isso seria uma busca vetorial (embeddings + similaridade)."""
    palavras_pergunta = set(pergunta.lower().split())
    pontuados = []
    for doc in documentos:
        palavras_doc = set(doc.lower().split())
        score = len(palavras_pergunta & palavras_doc)
        pontuados.append((score, doc))
    pontuados.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in pontuados[:top_k] if score > 0]


def responder_com_rag(pergunta: str) -> str:
    contexto = buscar_documentos_relevantes(pergunta, documentos)
    contexto_formatado = "\n".join(f"- {doc}" for doc in contexto)

    prompt = f"""\
Responda à pergunta do cliente usando APENAS as informações abaixo. Se a resposta não
estiver nas informações fornecidas, diga que não tem essa informação — não invente.

Informações disponíveis:
{contexto_formatado}

Pergunta do cliente: {pergunta}
"""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


if __name__ == "__main__":
    pergunta = "Posso devolver um produto depois de duas semanas?"
    print(responder_com_rag(pergunta))

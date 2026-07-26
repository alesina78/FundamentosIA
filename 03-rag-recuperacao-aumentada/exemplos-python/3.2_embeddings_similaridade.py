"""
A Anthropic não tem um endpoint próprio de embeddings — a parceira recomendada
oficialmente é a Voyage AI (voyageai.com), que tem free tier para começar.

pip install voyageai
"""
import hashlib
import json
import math
import re
from pathlib import Path

import anthropic
import voyageai
from pypdf import PdfReader

vo = voyageai.Client()
claude = anthropic.Anthropic()

CACHE_PATH = Path(__file__).parent / "embeddings_cache.json"
PDF_PATH = Path(__file__).parent / "politica_vestte_moda.pdf"


def carregar_documentos_do_pdf(caminho_pdf: Path) -> list[str]:
    """Extrai o texto do PDF e separa em documentos, um por seção numerada (ex: '1. Titulo')."""
    texto = "\n".join(pagina.extract_text() for pagina in PdfReader(caminho_pdf).pages)
    secoes = re.split(r"\n(?=\d+\.\s)", texto)
    return [secao.strip() for secao in secoes if re.match(r"\d+\.\s", secao.strip())]


documentos = carregar_documentos_do_pdf(PDF_PATH)


def _hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _carregar_cache() -> dict[str, list[float]]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def _obter_embeddings_com_cache(textos: list[str], input_type: str) -> list[list[float]]:
    """Retorna os embeddings dos textos, buscando no cache local (por hash individual) e
    chamando a API apenas para os textos que ainda não foram vistos."""
    cache = _carregar_cache()

    hashes = [_hash_texto(texto) for texto in textos]
    faltantes = [texto for texto, h in zip(textos, hashes) if h not in cache]

    if faltantes:
        novos_embeddings = vo.embed(faltantes, model="voyage-3.5", input_type=input_type).embeddings
        for texto, embedding in zip(faltantes, novos_embeddings):
            cache[_hash_texto(texto)] = embedding
        CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")

    return [cache[h] for h in hashes]


def obter_embeddings_documentos(documentos: list[str]) -> list[list[float]]:
    return _obter_embeddings_com_cache(documentos, input_type="document")


def cosseno(a: list[float], b: list[float]) -> float:
    produto_escalar = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    return produto_escalar / (norma_a * norma_b)


def buscar_por_similaridade(pergunta: str, documentos: list[str], top_k: int = 2) -> list[str]:
    embeddings_docs = obter_embeddings_documentos(documentos)
    embedding_pergunta = _obter_embeddings_com_cache([pergunta], input_type="query")[0]

    pontuados = [
        (cosseno(embedding_pergunta, emb_doc), doc)
        for emb_doc, doc in zip(embeddings_docs, documentos)
    ]
    pontuados.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in pontuados[:top_k]]


def responder_pergunta(pergunta: str, documentos: list[str], usar_ia: bool = True) -> str:
    """Busca os trechos mais relevantes (retrieval) e, se usar_ia=True, pede ao Claude uma
    resposta baseada neles (generation). Com usar_ia=False, retorna os trechos brutos do
    documento, sem passar pela LLM — útil para comparar os dois retornos."""
    trechos_relevantes = buscar_por_similaridade(pergunta, documentos)
    contexto = "\n\n".join(trechos_relevantes)

    if not usar_ia:
        return contexto

    system_prompt = (
        "Você é um assistente de atendimento ao cliente de uma loja de roupas. "
        "Responda a pergunta do usuário usando APENAS as informações do contexto fornecido. "
        "Se a resposta não estiver no contexto, diga que não sabe."
    )

    resposta = claude.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"}],
    )
    return resposta.content[0].text


if __name__ == "__main__":
    pergunta = "Posso trocar uma camisa que comprei?"

    print("=== Retorno bruto do documento (sem IA) ===")
    print(responder_pergunta(pergunta, documentos, usar_ia=False))

    print("\n=== Resposta gerada pela IA (com IA) ===")
    print(responder_pergunta(pergunta, documentos, usar_ia=True))

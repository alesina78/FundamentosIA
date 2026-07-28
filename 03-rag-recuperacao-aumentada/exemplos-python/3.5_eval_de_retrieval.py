"""
Eval de retrieval: mede o recall@k de duas estratégias de indexação sobre o MESMO dataset
de perguntas, e separa falha de retrieval de falha de geração.

Usa o mesmo PDF da aula 3.2 (politica_vestte_moda.pdf) e o mesmo cache local de embeddings
— rodar este script depois do 3.2 aproveita os embeddings já pagos.

pip install voyageai pypdf anthropic
"""
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path

import anthropic
import voyageai
from pypdf import PdfReader

vo = voyageai.Client()
claude = anthropic.Anthropic()

CACHE_PATH = Path(__file__).parent / "embeddings_cache.json"
PDF_PATH = Path(__file__).parent / "politica_vestte_moda.pdf"

# Dataset de avaliação. Para cada pergunta:
#   - secao_esperada: qual seção do documento CONTÉM a resposta (gabarito do retrieval)
#   - termo_esperado: termo que uma resposta correta obrigatoriamente menciona
#                     (gabarito da geração — critério determinístico, ver aula 2.4)
# As perguntas são escritas com o vocabulário do usuário, não o do documento: quem pergunta
# diz "devolver", não "política de reembolso". Um dataset que repete as palavras do
# documento infla o recall e esconde justamente o problema que o embedding deveria resolver.
DATASET = [
    ("Posso devolver uma peça duas semanas depois de comprar?", 1, "30"),
    ("Em quantos dias o dinheiro volta pro meu cartão?", 1, "10"),
    ("Vocês atendem no domingo?", 2, "segunda"),
    ("Até que horas o suporte funciona?", 2, "18"),
    ("A partir de quanto não pago entrega?", 3, "150"),
    ("A camisa ficou apertada, consigo trocar por outro número?", 4, "15"),
    ("Preciso guardar a etiqueta para trocar de tamanho?", 4, "etiqueta"),
    ("Comprei um biquíni e não serviu, tem troca?", 5, "higiene"),
    ("Abri o lacre da cueca, ainda dá pra devolver?", 5, "lacre"),
    ("Se a peça vier com defeito de fábrica, o que acontece?", 5, "defeito"),
]


# --------------------------------------------------------------------------------------
# Embeddings (mesma mecânica de cache da aula 3.2)
# --------------------------------------------------------------------------------------
def _hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _obter_embeddings_com_cache(textos: list[str], input_type: str) -> list[list[float]]:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}

    hashes = [_hash_texto(t) for t in textos]
    faltantes = [t for t, h in zip(textos, hashes) if h not in cache]

    if faltantes:
        novos = vo.embed(faltantes, model="voyage-3.5", input_type=input_type).embeddings
        for texto, embedding in zip(faltantes, novos):
            cache[_hash_texto(texto)] = embedding
        CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")

    return [cache[h] for h in hashes]


def cosseno(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    )


# --------------------------------------------------------------------------------------
# Duas estratégias de indexação (aula 3.3), cada chunk rotulado com sua seção de origem
# --------------------------------------------------------------------------------------
def texto_completo() -> str:
    return "\n".join(pagina.extract_text() for pagina in PdfReader(PDF_PATH).pages)


def indexar_por_secao() -> list[tuple[int, str]]:
    """Um chunk por seção numerada. Devolve pares (numero_da_secao, texto)."""
    partes = re.split(r"\n(?=\d+\.\s)", texto_completo())
    chunks = []
    for parte in partes:
        parte = parte.strip()
        m = re.match(r"(\d+)\.\s", parte)
        if m:
            chunks.append((int(m.group(1)), parte))
    return chunks


def indexar_por_tamanho_fixo(tamanho: int = 300, sobreposicao: int = 50) -> list[tuple[int, str]]:
    """Blocos de tamanho fixo com sobreposição, rotulados pela seção onde cai o meio do bloco.
    O rótulo é o que permite comparar as duas estratégias contra o mesmo gabarito."""
    texto = texto_completo()

    # Offset inicial de cada seção no texto completo, para saber a que seção pertence um bloco.
    fronteiras = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^(\d+)\.\s", texto)]

    def secao_do_offset(offset: int) -> int:
        secao = 0  # 0 = cabeçalho do documento, antes da primeira seção
        for inicio, numero in fronteiras:
            if inicio <= offset:
                secao = numero
        return secao

    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = min(inicio + tamanho, len(texto))
        bloco = texto[inicio:fim].strip()
        if bloco:
            chunks.append((secao_do_offset((inicio + fim) // 2), bloco))
        inicio += tamanho - sobreposicao
    return chunks


def buscar(pergunta: str, chunks: list[tuple[int, str]], k: int) -> list[int]:
    """Devolve as seções dos k chunks mais similares, na ordem do ranking."""
    embeddings = _obter_embeddings_com_cache([texto for _, texto in chunks], "document")
    emb_pergunta = _obter_embeddings_com_cache([pergunta], "query")[0]

    ranking = sorted(
        (
            (cosseno(emb_pergunta, emb), secao)
            for emb, (secao, _) in zip(embeddings, chunks)
        ),
        key=lambda x: x[0],
        reverse=True,
    )
    return [secao for _, secao in ranking[:k]]


# --------------------------------------------------------------------------------------
# Métrica 1 — recall@k por estratégia
# --------------------------------------------------------------------------------------
def recall_em_k(chunks: list[tuple[int, str]], k: int) -> float:
    """Fração das perguntas em que a seção correta aparece entre os k chunks recuperados.
    É o teto do que a geração pode acertar: o que o retrieval não trouxe, o modelo não tem."""
    acertos = sum(
        1 for pergunta, secao_esperada, _ in DATASET
        if secao_esperada in buscar(pergunta, chunks, k)
    )
    return acertos / len(DATASET)


def comparar_estrategias() -> None:
    estrategias = {
        "Por seção": indexar_por_secao(),
        "Tamanho fixo (300/50)": indexar_por_tamanho_fixo(),
    }

    print("=== recall@k por estratégia de indexação ===")
    print(f"{'Estratégia':<24} {'chunks':>7} {'@1':>7} {'@2':>7} {'@3':>7}")
    for nome, chunks in estrategias.items():
        valores = " ".join(f"{recall_em_k(chunks, k):>6.0%}" for k in (1, 2, 3))
        print(f"{nome:<24} {len(chunks):>7} {valores}")

    print(
        "\nrecall@k sobe com k por construção — recuperar mais chunks aumenta a chance de\n"
        "incluir o certo, ao custo de mais tokens e mais ruído no contexto. A pergunta útil\n"
        "não é 'qual k dá o maior recall', é 'qual o menor k com recall aceitável'."
    )


# --------------------------------------------------------------------------------------
# Métrica 2 — o diagnóstico que importa: falhou o retrieval ou a geração?
# --------------------------------------------------------------------------------------
def _normalizar(texto: str) -> str:
    """Remove acentos e caixa — o PDF de exemplo não tem acentuação."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def responder(pergunta: str, chunks: list[tuple[int, str]], k: int = 2) -> tuple[list[int], str]:
    secoes = buscar(pergunta, chunks, k)
    por_secao = {secao: texto for secao, texto in chunks}
    contexto = "\n\n".join(por_secao[s] for s in secoes if s in por_secao)

    r = claude.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        temperature=0,
        system=(
            "Responda usando APENAS o contexto fornecido. "
            "Se a resposta não estiver no contexto, diga apenas que não tem essa informação."
        ),
        messages=[{"role": "user", "content": f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"}],
    )
    return secoes, r.content[0].text


def diagnosticar(k: int = 2) -> None:
    """Classifica cada caso em: OK, falha de RETRIEVAL ou falha de GERAÇÃO.

    A distinção é o ponto central desta aula — sem ela, você acaba reescrevendo o prompt
    quando o problema estava no chunking (ou vice-versa).
    """
    chunks = indexar_por_secao()
    contagem = {"ok": 0, "retrieval": 0, "geracao": 0}

    print(f"\n=== Diagnóstico por caso (estratégia: por seção, k={k}) ===")
    for pergunta, secao_esperada, termo_esperado in DATASET:
        secoes, resposta = responder(pergunta, chunks, k)

        recuperou = secao_esperada in secoes
        respondeu = _normalizar(termo_esperado) in _normalizar(resposta)

        if not recuperou:
            # A seção com a resposta não chegou ao contexto: culpa do retrieval, não do prompt.
            categoria, detalhe = "FALHA RETRIEVAL", f"esperava seção {secao_esperada}, trouxe {secoes}"
            contagem["retrieval"] += 1
        elif not respondeu:
            # O contexto certo estava lá e a resposta ainda saiu errada: aí sim é geração.
            categoria, detalhe = "FALHA GERAÇÃO", f"sem o termo {termo_esperado!r} na resposta"
            contagem["geracao"] += 1
        else:
            categoria, detalhe = "OK", ""
            contagem["ok"] += 1

        print(f"  [{categoria:<15}] {pergunta}")
        if detalhe:
            print(f"{'':<20}{detalhe}")

    print(
        f"\n  OK: {contagem['ok']}/{len(DATASET)} | "
        f"falhas de retrieval: {contagem['retrieval']} | "
        f"falhas de geração: {contagem['geracao']}"
    )
    print(
        "\n  Onde agir: falha de retrieval → chunking, k, modelo de embedding, reranking.\n"
        "             falha de geração  → prompt, formato do contexto, modelo maior."
    )


if __name__ == "__main__":
    comparar_estrategias()
    diagnosticar()

"""
Padrão orquestrador-trabalhador (orchestrator-worker) implementado com chamadas
separadas à API — cada "agente" é só uma chamada com um system prompt e objetivo
diferentes. Não usa nenhuma API específica de multi-agente; a orquestração é o
código Python decidindo quem chama quem.
"""
import anthropic

client = anthropic.Anthropic()


def agente_pesquisador(topico: str) -> str:
    """Agente especializado: levanta pontos-chave sobre um tópico."""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system="Você é um pesquisador. Liste de 3 a 5 pontos-chave sobre o tópico, "
               "de forma objetiva, sem introdução nem conclusão.",
        messages=[{"role": "user", "content": topico}],
    )
    return r.content[0].text


def agente_redator(topico: str, pontos_chave: str) -> str:
    """Agente especializado: transforma pontos-chave em um parágrafo coeso."""
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system="Você é um redator. Transforme os pontos-chave fornecidos em um único "
               "parágrafo fluido e bem escrito, sem usar bullet points.",
        messages=[{
            "role": "user",
            "content": f"Tópico: {topico}\n\nPontos-chave:\n{pontos_chave}",
        }],
    )
    return r.content[0].text


def orquestrador(topico: str) -> str:
    """O 'coordenador': decide a sequência de agentes e repassa o resultado de um
    para o próximo. Aqui a orquestração é sequencial e fixa (pesquisador -> redator),
    mas poderia ser dinâmica (o próprio LLM decidindo quem chamar via tool use)."""
    print("--- Agente pesquisador trabalhando ---")
    pontos_chave = agente_pesquisador(topico)
    print(pontos_chave)

    print("\n--- Agente redator trabalhando ---")
    texto_final = agente_redator(topico, pontos_chave)
    return texto_final


if __name__ == "__main__":
    resultado = orquestrador("Benefícios de RAG para aplicações empresariais")
    print("\n--- Resultado final ---")
    print(resultado)

# Módulo 3 — RAG (Retrieval-Augmented Generation)

> Nível: Intermediário · Primeira arquitetura do curso: o LLM deixa de responder sozinho e
> passa a consultar uma base de conhecimento.

## Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- Explicar o que é RAG e por que ele reduz alucinações e traz conhecimento atualizado/privado.
- Entender embeddings, similaridade vetorial e o papel de um vector database.
- Escolher uma estratégia de chunking adequada ao tipo de conteúdo.
- Decidir entre RAG, fine-tuning e long context para um problema real.
- Implementar um pipeline RAG simples em Python (embeddings + retrieval + geração).

## Estrutura do Módulo

| # | Aula |
|---|------|
| 3.1 | [Conceitos: retrieval + generation](3.1-conceitos-retrieval-generation.md) |
| 3.2 | [Embeddings e vector databases](3.2-embeddings-vector-databases.md) |
| 3.3 | [Chunking e estratégias de indexação](3.3-chunking-estrategias-indexacao.md) |
| 3.4 | [RAG vs fine-tuning vs long context](3.4-rag-vs-fine-tuning-vs-long-context.md) |

## Cadastro e Configuração de Ambiente — Voyage AI

Os exemplos deste módulo usam a **Voyage AI** para gerar embeddings, já que a Anthropic
não oferece endpoint próprio para isso (veja [aula 3.2](3.2-embeddings-vector-databases.md)).

1. Crie uma conta gratuita em [voyageai.com](https://www.voyageai.com/) (há free tier para começar).
2. Gere uma API key no painel da Voyage AI.
3. Exporte a key como variável de ambiente:

   ```bash
   export VOYAGE_API_KEY="sua-api-key-aqui"
   ```

   No Windows (PowerShell):

   ```powershell
   $env:VOYAGE_API_KEY = "sua-api-key-aqui"
   ```

4. Instale o SDK Python:

   ```bash
   pip install voyageai
   ```

5. Teste a configuração:

   ```python
   import voyageai

   vo = voyageai.Client()  # lê VOYAGE_API_KEY do ambiente
   resultado = vo.embed(["teste"], model="voyage-3.5", input_type="document")
   print(len(resultado.embeddings[0]))  # dimensão do embedding
   ```

## Documentação Oficial (pt-BR/EN)

- [Anthropic — Building with Claude: Retrieval](https://docs.claude.com/en/docs/build-with-claude/embeddings)
- [Anthropic Academy — RAG](https://www.anthropic.com/learn)

## Pré-requisitos

[Módulo 2 — Prompt Engineering](../02-prompt-engineering/README.md)

---
[← Módulo anterior](../02-prompt-engineering/README.md) | [Início do curso](../README.md) | [Próximo módulo →](../04-agentes-e-tool-use/README.md)

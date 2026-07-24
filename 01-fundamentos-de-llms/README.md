# Módulo 1 — Fundamentos de LLMs

> Nível: Iniciante · Base para todos os módulos seguintes.

## Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- Explicar em alto nível como um LLM gera texto (previsão de próximo token).
- Calcular e estimar custo/latência a partir de tokens e context window.
- Reconhecer os principais tipos de limitação e alucinação de um LLM.
- Decidir quando um LLM sozinho é (ou não) a ferramenta certa para um problema.

## Estrutura do Módulo

| # | Aula |
|---|------|
| 1.1 | [O que são LLMs e como funcionam](1.1-o-que-sao-llms-como-funcionam.md) |
| 1.2 | [Tokens, context window e custos](1.2-tokens-context-window-custos.md) |
| 1.3 | [Limitações, alucinações e quando desconfiar](1.3-limitacoes-alucinacoes.md) |

## Setup — API Key da Anthropic

Os exemplos em Python deste módulo chamam a API da Anthropic, então você vai precisar de
uma API key antes de começar:

1. Crie uma conta em [console.anthropic.com](https://console.anthropic.com/).
2. Gere uma chave em **API Keys**.
3. Configure como variável de ambiente: `ANTHROPIC_API_KEY=sua_chave_aqui`.
4. Instale o SDK: `pip install anthropic`.

Contas novas costumam receber créditos gratuitos iniciais, e os exemplos deste módulo usam
poucas chamadas curtas — custo total da ordem de centavos de dólar.

**Alternativa 100% gratuita:** se preferir não usar créditos pagos, o
[Google AI Studio](https://aistudio.google.com/) oferece uma API key gratuita (Gemini) com
free tier generoso para uso educacional. O SDK muda (`pip install google-generativeai` em
vez de `anthropic`) e a sintaxe das chamadas é diferente da usada nos exemplos deste curso
— sirva-se dela para experimentar os conceitos (tokens, context window, alucinação) na
prática sem custo, adaptando o código dos exemplos à API do Gemini.

## Documentação Oficial (pt-BR/EN)

- [Anthropic — Documentação da API](https://docs.claude.com/)
- [Anthropic — Modelos Claude](https://docs.claude.com/en/docs/about-claude/models)

## Pré-requisitos

Nenhum — ponto de partida do curso.

---
[Início do curso](../README.md) | [Próximo módulo →](../02-prompt-engineering/README.md)

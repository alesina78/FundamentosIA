# IA na Prática para Devs

> Curso livre, em português, para desenvolvedores aprenderem a usar IA de forma correta,
> segura e eficiente no dia a dia — de prompt engineering a agentes, RAG, MCP, ferramentas
> agentic coding (harness) e desenvolvimento guiado por especificação (SDD).

## Sobre o Curso

| | |
|---|---|
| **Público-alvo** | Desenvolvedores(as) de software, técnicos, com experiência prévia em programação |
| **Formato** | Repositório Markdown self-paced (aulas com exemplos práticos em Python) |
| **Linguagem dos exemplos** | Python (sempre que possível, exemplos práticos executáveis) |
| **Pré-requisitos** | Conhecimento básico de Python; não é necessária experiência prévia com IA |
| **Fontes** | Documentação oficial da Anthropic e do MCP; curso independente, sem vínculo com a Anthropic |

## Módulos do Curso

| # | Módulo | Nível |
|---|--------|-------|
| 1 | [Fundamentos de LLMs](01-fundamentos-de-llms/README.md) | Iniciante |
| 2 | [Prompt Engineering](02-prompt-engineering/README.md) | Iniciante |
| 3 | [RAG — Retrieval-Augmented Generation](03-rag-recuperacao-aumentada/README.md) | Intermediário |
| 4 | [Agentes de IA e Tool Use](04-agentes-e-tool-use/README.md) | Intermediário |
| 5 | [MCP — Model Context Protocol](05-mcp-model-context-protocol/README.md) | Intermediário |
| 6 | [Harness e Agentic Coding Tools](06-harness-agentic-coding-tools/README.md) | Avançado |
| 7 | [SDD — Spec-Driven Development](07-sdd-spec-driven-development/README.md) | Intermediário |
| 8 | [Boas Práticas e Uso Responsável](08-boas-praticas-uso-responsavel/README.md) | Todos os níveis |
| 9 | [Fluxo de Trabalho na Prática](09-fluxo-de-trabalho-na-pratica/README.md) | Avançado |

## O Arco do Curso

O curso tem duas partes, e vale saber disso desde o começo porque a **perspectiva muda** entre
elas:

**Parte I — Construir com IA (módulos 1 a 5).** Você está do lado de quem constrói: chama a
API, escreve prompts, monta um pipeline RAG, implementa um agente com tool use e expõe
ferramentas por MCP. O sistema em estudo é o que você programa.

**Parte II — Trabalhar com IA (módulos 6 a 9).** O objeto de estudo passa a ser a ferramenta
que você usa para programar, e o seu próprio processo: o harness (módulo 6), a metodologia de
pedir (módulo 7), o uso responsável (módulo 8) e o fluxo de trabalho completo (módulo 9).

A ordem não é acidental. Um harness de agentic coding **é** um loop agentic com permissões e
gestão de contexto — as mesmas peças do módulo 4. Quem construiu um agente não vê o Claude
Code como uma caixa mágica cheia de features, e sim como engenharia reconhecível: sabe por que
uma skill economiza contexto, por que um hook é mais confiável que uma instrução no prompt, e
onde intervir quando o agente faz algo inesperado.

## Sobre as Fontes

Este é um **curso independente**, sem vínculo com a Anthropic. Não é material oficial, não
prepara para nenhuma prova e não emite certificado.

O conteúdo é escrito a partir da documentação pública oficial — a documentação da API da
Anthropic, a especificação do Model Context Protocol e os guias de engenharia da própria
Anthropic — mais experiência prática de uso das ferramentas. Cada aula termina com os links
das fontes que a embasam, para você conferir na origem e acompanhar atualizações.

Se você procura certificação oficial ou cursos com certificado, o caminho é a **Anthropic
Academy**, que oferece material oficial gratuito sobre MCP, Claude API e Claude Code.

## Documentação Oficial

- [Anthropic — Documentação da API](https://docs.claude.com/)
- [Anthropic Academy](https://www.anthropic.com/learn)
- [Model Context Protocol — Especificação](https://modelcontextprotocol.io/)

## Pré-requisitos

- Python básico (variáveis, funções, requisições HTTP com `requests`).
- Uma chave de API da Anthropic (ou de outro provedor) para rodar os exemplos práticos —
  os módulos indicam alternativas com camada gratuita quando existirem.
- Git e um editor de código.

## Como Usar Este Curso

1. Siga os módulos na ordem — cada um assume conceitos dos anteriores.
2. Rode os exemplos em Python de cada aula; não apenas leia o código.
3. Ao final, o módulo 9 conecta tudo num fluxo de trabalho real de desenvolvimento com IA.

## Licença

Conteúdo educacional de uso livre. Curso independente, sem vínculo com a Anthropic —
"Claude" e "Anthropic" são marcas de seus respectivos donos. Verifique sempre a documentação
oficial para informações atualizadas sobre produtos, modelos e preços.

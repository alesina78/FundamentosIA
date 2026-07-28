# Módulo 6 — Harness e Agentic Coding Tools

> Nível: Avançado · A virada do curso: do agente que você constrói para a ferramenta que
> você usa (ex: Claude Code).

## A virada do curso: deste módulo em diante, o objeto de estudo muda

Nos módulos 1 a 5 você esteve do lado de quem **constrói**: chamou a API, escreveu prompts,
montou um pipeline RAG, implementou um loop agentic com tool use e expôs ferramentas por MCP.
O sistema em estudo era o que você programava.

A partir daqui a perspectiva se inverte: o objeto de estudo passa a ser **a ferramenta que
você usa para programar** — e o seu próprio jeito de trabalhar com ela.

A boa notícia é que não há conhecimento novo a decorar, e sim reaproveitamento direto: um
harness *é* o loop agentic da aula 4.2 embrulhado em permissões e gestão de contexto. Você vai
reconhecer cada peça:

| Peça do harness | Onde você já viu |
|---|---|
| Loop agentic (raciocinar → agir → observar) | Aula 4.2 |
| Tool use sobre arquivos e shell | Aula 4.1 |
| Skills (contexto carregado sob demanda) | Módulo 3 — é o princípio do RAG aplicado a instruções |
| Subagents | Aula 4.3 — multi-agente, integrado ao harness |
| Servidores MCP como extensão | Módulo 5 |
| Gestão da janela de contexto | Aula 1.2 |

É por isso que este módulo vem depois de construir um agente, e não antes: quem já escreveu
um loop agentic não vê o Claude Code como mágica, vê como engenharia — e sabe onde intervir
quando o comportamento não é o esperado.

## Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- Explicar o que é um "harness" de agentic coding (ex: Claude Code) e como ele difere de
  um chat comum com IA.
- Descrever o papel de hooks, skills e subagents num harness.
- Configurar permissions de forma segura (o que o agente pode executar sem confirmação).
- Avaliar riscos de dar autonomia a um agente sobre um repositório real.

## Estrutura do Módulo

| # | Aula |
|---|------|
| 6.1 | [O que é um harness de agentic coding](6.1-o-que-e-um-harness.md) |
| 6.2 | [Hooks, skills e subagents](6.2-hooks-skills-subagents.md) |
| 6.3 | [Permissions e segurança](6.3-permissions-e-seguranca.md) |

## Documentação Oficial (pt-BR/EN)

- [Anthropic — Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Anthropic — Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [SkillsMP — Marketplace de Skills](https://skillsmp.com/)

## Pré-requisitos

[Módulo 5 — MCP](../05-mcp-model-context-protocol/README.md)

---
[← Módulo anterior](../05-mcp-model-context-protocol/README.md) | [Início do curso](../README.md) | [Próximo módulo →](../07-sdd-spec-driven-development/README.md)

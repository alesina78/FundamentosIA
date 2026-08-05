# Módulo 5 — MCP (Model Context Protocol)

> Nível: Intermediário · Como as ferramentas do módulo 4 deixam de viver dentro do seu
> código e passam a ser reutilizáveis por qualquer cliente.

## Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- Explicar o que é o MCP e o problema que ele resolve (padronizar acesso a dados/ferramentas).
- Descrever a arquitetura cliente-servidor do MCP (host, client, server).
- Criar um servidor MCP simples em Python expondo uma ferramenta.
- Decidir quando vale a pena construir um servidor MCP vs uma integração direta.
- Expor um banco Postgres real (hospedado no Render) como servidor MCP, com acesso somente-leitura.

## Estrutura do Módulo

| # | Aula |
|---|------|
| 5.1 | [Conceito e arquitetura cliente-servidor](5.1-conceito-arquitetura-cliente-servidor.md) |
| 5.2 | [Criando um servidor MCP simples em Python](5.2-criando-servidor-mcp-python.md) |
| 5.3 | [Quando e como integrar MCP nos seus workflows](5.3-quando-integrar-mcp.md) |
| 5.4 | [Lab: um servidor MCP sobre um Postgres real](5.4-lab-mcp-postgres-render.md) |

## Documentação Oficial (pt-BR/EN)

- [Model Context Protocol — Especificação](https://modelcontextprotocol.io/)
- [Anthropic — MCP Connectors](https://docs.claude.com/en/docs/agents-and-tools/mcp-connector)

## Pré-requisitos

[Módulo 4 — Agentes de IA e Tool Use](../04-agentes-e-tool-use/README.md)

---
[← Módulo anterior](../04-agentes-e-tool-use/README.md) | [Início do curso](../README.md) | [Próximo módulo →](../06-harness-agentic-coding-tools/README.md)

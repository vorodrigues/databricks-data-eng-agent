---
name: plan
description: Gera um plano faseado em .data-eng/plans/ a partir de uma SPEC, com tarefas, criterios de sucesso e links de documentacao por fase, na mesma profundidade da SPEC. Use quando o usuario pedir um plano ou plano de implementacao a partir de uma SPEC de modelo de dados.
---

# plan

Gera um plano faseado para implementar a SPEC, em markdown puro (Write/Edit; sem wikilinks — referencie por caminho relativo).

## Onde gravar

Grave em `.data-eng/plans/`. Liste o diretorio antes e escolha o proximo nome livre:
- Plano novo: `PLAN-<n>.md` (`n` = maior existente + 1).
- Revisao: `PLAN-<n>-<r>.md`.

Planos sao **imutaveis**: nunca edite nem sobrescreva um existente — se o nome ja existe, incremente.

## Estrutura obrigatoria

- **Fontes**: caminhos da SPEC, planos/outputs anteriores relevantes e guidelines.
- **Padroes fundamentais**: convencoes herdadas das guidelines + decisoes transversais da SPEC (determinismo, incrementalidade/idempotencia, contratos de tabela/coluna, evidencias em `PLAN-N_OUT`).
- **Mapa de fases**: tabela Fase | Entrega | Bloqueia. Cada entrega referencia uma secao da SPEC.
- **Uma secao por fase** contendo:
    - Objetivo (1–2 frases).
    - Tarefas: checklist curto de acoes executaveis, uma por linha, referenciando a secao da SPEC que define O QUE (por caminho: `specs/SPEC-N.md#secao`). Nao repita o conteudo da SPEC.
    - Criterios de sucesso: priorize verificacoes rapidas e deterministicas (ex.: `validate_state.py` sem diff; contagem de linhas apos MERGE estavel entre reexecucoes; contratos de comentario/PK/PII presentes).
- **Fora de escopo**: espelha a secao homonima da SPEC.

## Ordem tipica das fases (medallion)

Bronze (estado + ingestao CDC) -> Silver (estado + limpeza no CDC) -> Gold (estado + transformacoes/SCD Tipo 1) -> Orquestracao (bundle/job serverless) -> Validacao end-to-end.

## Regras de profundidade

Mesma profundidade da SPEC. Tarefas descrevem O QUE entregar, nao COMO implementar. Adicione links da documentacao Databricks das funcionalidades REQUERIDAS.

SPEC:
$ARGUMENTS

Se nenhuma SPEC foi fornecida acima, pergunte ao usuario.

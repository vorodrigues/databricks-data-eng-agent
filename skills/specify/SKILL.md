---
name: specify
description: Valida o estado e escreve uma nova SPEC em .data-eng/specs/ com o incremental das alteracoes ao modelo de dados (bronze/silver/gold e transformacoes de ingestao). Use quando o usuario pedir para escrever, criar ou incrementar uma SPEC de mudancas no modelo de dados.
---

# specify

Escreve uma SPEC das alteracoes solicitadas ao modelo de dados fonte e/ou destino, em markdown puro (use Write/Edit; sem wikilinks — referencie por caminho relativo).

## Pre-requisito: validacao do estado

Antes de especificar, execute a skill `validate-state`. Se houver **DIFF ENCONTRADO**, apresente o relatorio e resolva o conflito com o usuario antes de escrever a SPEC. Nao especifique sobre um estado divergente.

## Onde gravar

Grave em `.data-eng/specs/`. Liste o diretorio antes e escolha o proximo nome livre:
- SPEC nova: `SPEC-<n>.md` (`n` = maior existente + 1).
- Revisao: `SPEC-<n>-<r>.md`.

SPECs sao **imutaveis**: nunca edite nem sobrescreva uma existente — se o nome ja existe, incremente. No topo, inclua uma secao `## Fontes` com os caminhos relativos das origens (SPEC anterior, outputs, guidelines).

## Conteudo

Esta SPEC contem apenas o **incremental** em relacao aos outputs anteriores em `.data-eng/outputs/`. Especifique **O QUE** (contratos, schemas, criterios verificaveis, nomes de artefatos), nao O COMO (bibliotecas, layout de codigo). Cubra, para as solicitacoes do usuario:

- Alteracoes do estado local da camada **bronze** (modelo fonte).
- Alteracoes do estado local da camada **silver** (identico a fonte, limpo).
- Alteracoes as **transformacoes da ingestao silver** (limpeza dentro do CDC).
- Alteracoes do estado local da camada **gold** (modelo destino, star schema SCD Tipo 1; ou OBT/wide).
- Alteracoes as **transformacoes da ingestao gold** (agregacoes, metricas, negocio).
- **Metric Views**, **Genie spaces**, **Data Classification** e **Quality Monitor**, quando solicitados.

Para cada tabela afetada, fixe os contratos obrigatorios: comentario e chave primaria (FK opcional) da tabela; comentario e classificacao de PII de cada coluna. Para Metric Views: comentario da view e, para cada dimensao/medida, comentario e classificacao de PII. Registre so a decisao final (sem conflitos/alternativas). Seja sucinto. Inclua uma secao "Fora de escopo". Nao inclua criterios de sucesso.

## Base de conhecimento (KB): consultar antes de detalhar

Antes de descrever colunas de uma tabela bronze (SAP) ou de um data product (gold), verifique se ela ja existe na KB do plugin — **sem** carregar as definicoes no contexto:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb.py" find <nome_da_tabela>
```

- **Se constar na KB**: **nao** detalhe colunas na SPEC. Apenas **referencie** o arquivo da KB (o caminho impresso pelo `find`, ex.: `knowledge/sap/bronze/kna1.yaml`) e registre que o `/run` deve **copia-lo deterministicamente** para `schemas/<camada>/<tabela>.yaml` (via `kb.py copy`). Anote so os ajustes incrementais especificos deste projeto, se houver.
- **Se nao constar**: especifique a tabela normalmente, com os contratos obrigatorios acima.

## Artefatos de semantica e governanca

Quando o usuario solicitar, especifique tambem (O QUE, nao O COMO), cada um como um arquivo de estado declarativo que o `/run` materializa com o notebook deterministico correspondente (ver `guidelines/LAYERS.md`):

- **Metric View** — `schemas/metric_views/<nome>.yaml` (fonte gold, joins, dimensoes, medidas; contratos de comentario/PII). Base semantica orientada as metricas de negocio.
- **Genie space** — `schemas/genie/<nome>.yaml` (titulo, tabelas/metric views expostas, instrucoes, perguntas), baseado nas Metric Views.
- **Data Classification** — `schemas/governanca/data_classification.yaml` (catalogo alvo).
- **Quality Monitor** — `schemas/governanca/<nome>.yaml` (objeto monitorado: schema ou tabela).

Use os exemplos em `${CLAUDE_PLUGIN_ROOT}/templates/schema/` como referencia de formato.

Solicitacoes:
$ARGUMENTS

Se nenhuma solicitacao foi fornecida acima, pergunte ao usuario.

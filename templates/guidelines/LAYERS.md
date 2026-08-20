# Padroes de camadas e determinismo

## Arquitetura medallion

- **Bronze** — modelo de dados FONTE. Dados brutos ingeridos diretamente do sistema
  originador, sem transformacao de negocio.
- **Silver** — modelo de dados IDENTICO a fonte, apos limpeza (tipos, trims, dedup,
  padronizacao). Mesmo grao e schema da bronze/fonte.
- **Gold** — modelo de dados DESTINO, orientado as necessidades de negocio. Star schema
  com dimensoes SCD Tipo 1 e fatos. Inclui a **Metric View** (camada semantica). Admite
  tambem tabelas **OBT/wide** (`entidade: obt`) — data products denormalizados que unem
  varias silvers (transformacao custom, `ingestao: custom`).

## Base de conhecimento (KB)

- O plugin traz definicoes pre-existentes de tabelas-fonte SAP (bronze) e data products
  (gold OBT) em `${CLAUDE_PLUGIN_ROOT}/knowledge/sap/{bronze,gold}/`, no formato do plugin.
- Consulta **eficiente** (sem carregar as definicoes no contexto): use o indice via
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/kb.py" find <nome>`.
- Se a tabela/data product consta na KB, a SPEC **referencia** o arquivo da KB e o `/run`
  o **copia deterministicamente** para `schemas/<camada>/` (`kb.py copy`), sem regerar colunas.

## Determinismo

- Use sempre o mesmo notebook parametrizado quando possivel:
    - `ingest_cdc.py` — ingestao CDC bronze -> silver (inclui a limpeza da silver).
    - `scd_type1.py` — modulo deterministico de dimensao SCD Tipo 1, consumido pelo gold.
    - `create_metric_view.py` — cria Metric View a partir de `schemas/metric_views/<nome>.yaml`.
    - `create_genie_space.py` — cria Genie space a partir de `schemas/genie/<nome>.yaml`.
    - `enable_data_classification.py` — ativa Data Classification no catalogo.
    - `create_quality_monitor.py` — cria Quality Monitor a partir de `schemas/governanca/<nome>.yaml`.
- Para excecoes, parta de `transform_gold.py` e faca a alteracao minima (agregacoes,
  metricas, joins de OBT e demais transformacoes de negocio ficam aqui).
- Toda ingestao e **incremental** (watermark) e **idempotente** (MERGE pela chave). Os
  recursos de governanca/semantica sao idempotentes (CREATE OR REPLACE / get-then-create).

## Contratos obrigatorios

- Toda **tabela** possui: comentario, chave primaria; chave estrangeira e opcional.
- Toda **coluna** possui: comentario e classificacao de PII
  (`nenhum` | `direto` | `indireto` | `sensivel`).
- Toda **Metric View** possui: comentario; e cada dimensao/medida possui comentario e
  classificacao de PII.
- O estado local (YAML em `schemas/`) e a fonte de verdade e deve refletir o Unity Catalog
  (validado por `validate_state.py`). Nunca hardcode catalogo/schema — parametrize.

## Fluxo de desenvolvimento

1. Atualize o estado e o codigo locais.
2. Valide o estado local x Unity Catalog.
3. Teste no workspace Databricks (prefira Serverless).

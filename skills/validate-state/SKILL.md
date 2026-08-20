---
name: validate-state
description: Valida deterministicamente o estado local dos schemas (YAML em schemas/) contra o Unity Catalog, rodando validate_state.py, e apresenta um relatorio de diffs. Use quando o usuario pedir para validar, conferir ou comparar o estado dos schemas local x remoto, ou como pre-requisito de specify.
allowed-tools: Bash, Read
---

# validate-state

Compara o estado local (definicoes YAML em `schemas/{bronze,silver,gold}/`) com o estado remoto (Unity Catalog). O diff e **deterministico**: quem o calcula e o script; voce apenas interpreta e reporta.

## Passos

1. Confirme que `databricks.yml` esta preenchido (fonte unica de config: `variables` com `catalog`/`schema_*`/`warehouse_id` e `targets.*.workspace` com `host`). Se houver `<PREENCHER>`, peca ao usuario para preencher antes de continuar. A auth (perfil da CLI) e local: garanta um `DATABRICKS_CONFIG_PROFILE` no ambiente ou informe `--profile`.
2. Rode o validador (da raiz do projeto, onde esta o `databricks.yml`):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_state.py"
   ```

   Opcoes: `--layer bronze|silver|gold` (uma camada); `--target <nome>` (default: target `default:true`, senao `dev`); `--profile <perfil>` (auth da CLI).

3. Interprete a saida:
   - **SEM DIFF** — estado sincronizado. Reporte e siga.
   - **DIFF ENCONTRADO** — apresente ao usuario o relatorio com **todos** os diffs, agrupados por categoria (tabelas, colunas, tipos, comentarios, nulabilidade, chaves, PII), e **peca para o usuario resolver o conflito** (ajustar o YAML local ou o Unity Catalog) antes de prosseguir. Nao decida sozinho qual lado esta correto.

O script sai com codigo 0 (sem diff) ou 1 (diff). Nao edite `schemas/` nem o Unity Catalog nesta skill — apenas reporte.

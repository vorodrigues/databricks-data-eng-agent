# Ambiente

Os valores concretos do ambiente (catalogo, schemas por camada, warehouse, host, profile,
root_path) vivem em **`databricks.yml`** — a **fonte unica de verdade**. Nao os duplique aqui
nem em outro lugar; leia-os do bundle (`variables` + o `target` escolhido).

- Local:
    - Diretorio raiz local: `./`
    - Estado local dos schemas: `schemas/{bronze,silver,gold}/` (um YAML por tabela).
    - Ciclo (specs/plans/outputs) e guidelines: `.data-eng/`.
- Databricks (config de projeto, em `databricks.yml`):
    - `variables`: `catalog`, `schema_bronze`, `schema_silver`, `schema_gold`, `warehouse_id`.
    - `targets.<dev|prod>.workspace`: `host`, `root_path`.
    - `validate_state.py` resolve esses valores automaticamente; sobrescreva por flag se preciso.
    - Prefira compute Serverless sempre que possivel.
- Auth (local, por usuario — NAO vai para o repo):
    - Perfil da Databricks CLI via `--profile` ou a variavel `DATABRICKS_CONFIG_PROFILE`.

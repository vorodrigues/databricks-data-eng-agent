---
name: init
description: Inicializa um projeto de engenharia de dados para o ciclo validate-state -> specify -> plan -> run — cria o scaffold (.data-eng/, schemas/, resources/, src/notebooks/, databricks.yml) com as guidelines e templates, e aplica as permissoes padrao em .claude/settings.json. Use quando o usuario pedir para inicializar, configurar ou preparar o projeto.
allowed-tools: Bash, Read, Glob
---

# init

Cria a estrutura que as demais skills deste plugin assumem e concede as permissoes que a skill `run` precisa para executar um plano end-to-end sem interrupcoes.

## Scaffold criado (na raiz do projeto de dados)

```
.data-eng/
├── specs/        # SPEC-N.md — o que/porque (markdown puro)
├── plans/        # PLAN-N.md — como/ordem (fases, tarefas, criterios)
├── outputs/      # PLAN-N_OUT.md — estado real da execucao
└── guidelines/   # GENERAL, CODING, ENV, LAYERS (o GENERATOR le tudo)
schemas/{bronze,silver,gold}/   # estado local: um YAML por tabela
resources/etl.job.yml           # job serverless bronze->silver->gold
src/notebooks/{ingest_cdc.py,scd_type1.py,transform_gold.py}   # notebooks deterministicos
databricks.yml                  # bundle DAB — fonte unica de config
.claude/settings.json           # permissoes (merge nao-destrutivo)
```

## Passos

1. Mostre o que sera feito, sem gravar nada:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/init.sh" --dry-run
   ```

2. Apresente o resultado ao usuario e confirme.
3. Aplique:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/init.sh"
   ```

4. Relate a saida e repasse os proximos passos que o script imprime.

O script e idempotente: preserva arquivos existentes (`cp -n`), faz uniao das listas de permissao com o que ja houver em `.claude/settings.json` e grava um `.bak` do arquivo anterior. Requer `jq`.

Nao crie arquivos alem dos que o script cria. Nao popule `schemas/`, `specs/` ou `plans/`.

## Depois do init

- Preencha os campos `<PREENCHER>` em `databricks.yml` (fonte unica de config: catalogo, schemas, warehouse, host, profile).
- Defina as tabelas de origem em `schemas/bronze/` (use os exemplos em `${CLAUDE_PLUGIN_ROOT}/templates/schema/` como referencia).

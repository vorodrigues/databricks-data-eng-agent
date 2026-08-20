# data-eng-agent

> Plugin do Claude Code para **spec-driven development** de pipelines de engenharia de dados no Databricks.

Especifica, planeja e desenvolve código **determinístico** para a arquitetura medallion
(bronze → silver → gold), mantendo um estado local declarativo (YAML) que é validado
deterministicamente contra o Unity Catalog. Métodos determinísticos executam as tarefas
sempre que possível; abordagens agênticas ficam reservadas às exceções.

---

## Objetivo

- **Especificar, planejar e executar** mudanças no modelo de dados por um ciclo auditável e incremental.
- **Manter uma fonte de verdade local** dos ativos (schemas YAML), validável contra o Unity Catalog.
- **Priorizar o determinismo**: notebooks parametrizados e reutilizáveis para tarefas recorrentes
  (CDC, SCD Tipo 1, Metric Views, Genie, Data Classification, Quality Monitor); agêntico só nas exceções.
- **Reaproveitar conhecimento**: base de conhecimento (KB) de tabelas-fonte SAP e data products
  já modelados, referenciados na SPEC e copiados deterministicamente na execução.
- **Governança por contrato**: toda tabela e coluna com comentário e classificação de PII; artefatos em PT-BR.

---

## Instalação

### Pré-requisitos

| Requisito | Detalhe |
|-----------|---------|
| **Claude Code** | Versão recente (recomendado v2.1.195+) com suporte a plugins e marketplaces. |
| **Databricks CLI** | Autenticada (perfil em `~/.databrickscfg`) e um SQL warehouse para a validação de estado. |
| **Python 3** | Com `pyyaml` instalado (usado pelos scripts e notebooks). |
| **jq** | Necessário para o `init.sh` (merge não-destrutivo de permissões). |
| **Git** | Acesso ao repositório público do plugin no GitHub. |

### Plugin

O plugin é distribuído como um **marketplace do Claude Code** no repositório
[`vorodrigues/databricks-data-eng-agent`](https://github.com/vorodrigues/databricks-data-eng-agent)
e pode ser instalado diretamente do GitHub.

**1. Adicione o marketplace e instale o plugin** (dentro do Claude Code):

```
/plugin marketplace add vorodrigues/databricks-data-eng-agent
/plugin install data-eng-agent@databricks-data-eng-agent
```

Quando solicitado, escolha o escopo (**User**, **Project** ou **Local**).

**Alternativa via CLI** (não-interativa):

```bash
claude plugin marketplace add vorodrigues/databricks-data-eng-agent
claude plugin install data-eng-agent@databricks-data-eng-agent
```

Para fixar uma versão específica, use a tag no marketplace: `.../databricks-data-eng-agent@v0.1.0`.

**2. Verifique e gerencie a instalação:**

```bash
claude plugin list                                     # lista plugins instalados
claude plugin enable  data-eng-agent@databricks-data-eng-agent
claude plugin disable data-eng-agent@databricks-data-eng-agent
claude plugin uninstall data-eng-agent@databricks-data-eng-agent
```

O menu interativo `/plugin` oferece as mesmas operações, e `/plugin marketplace update
databricks-data-eng-agent` atualiza o marketplace para a versão mais recente.

**3. Inicialize um projeto de dados** e siga o ciclo de trabalho:

```
/data-eng-agent:init
```

O `init` cria o scaffold (`.data-eng/`, `schemas/`, `resources/`, `src/notebooks/`,
`databricks.yml`) e aplica as permissões. Em seguida, preencha os campos `<PREENCHER>` em
`databricks.yml` (catálogo, schemas por camada, warehouse, host, profile).

> **Nota** — para ser instalável do GitHub, o repositório precisa conter
> `.claude-plugin/marketplace.json` (definindo o marketplace `databricks-data-eng-agent` e
> apontando para o plugin `data-eng-agent`) e o `.claude-plugin/plugin.json` do plugin.

---

## Ciclo de trabalho

```
validate-state  ->  specify   ->   plan    ->   run
 (diff local        (SPEC do       (plano       (ORCHESTRATOR +
  x Unity Catalog)   incremental)   faseado)     GENERATOR / EVALUATOR)
```

| Skill | O que faz |
|-------|-----------|
| `init` | Cria o scaffold do projeto e aplica as permissões. |
| `validate-state` | Roda `validate_state.py`: diff determinístico do estado local (YAML) × Unity Catalog; reporta e pede resolução de conflitos. |
| `specify` | Valida o estado e escreve uma SPEC incremental (bronze/silver/gold, transformações de ingestão, Metric Views, Genie, governança). Consulta a KB e referencia o que já existe. |
| `plan` | Gera um plano faseado com tarefas e critérios de sucesso verificáveis. |
| `run` | Executa o plano com o padrão ORCHESTRATOR / GENERATOR / EVALUATOR, registrando evidências. |

O `run` delega cada fase a subagentes isolados: o **GENERATOR** produz os entregáveis e o
**EVALUATOR** verifica cada critério de sucesso de forma independente; o ORCHESTRATOR é a
única ponte entre eles e decide quando avançar.

---

## Padrões

- **Camadas**
  - **Bronze** — modelo de dados fonte; dados brutos ingeridos diretamente do sistema originador.
  - **Silver** — modelo idêntico à fonte, após limpeza (tipos, trims, dedup, padronização).
  - **Gold** — modelo destino, orientado ao negócio; star schema com dimensões SCD Tipo 1 e fatos,
    e/ou tabelas OBT/wide (data products denormalizados). Inclui a Metric View.

- **Determinismo** — notebooks parametrizados e reutilizáveis: `ingest_cdc.py` (CDC bronze → silver,
  com a limpeza da silver), `scd_type1.py` (dimensão SCD Tipo 1, consumido por `transform_gold.py`),
  `create_metric_view.py`, `create_genie_space.py`, `enable_data_classification.py` e
  `create_quality_monitor.py`. Exceções partem de um template com alteração mínima.

- **Base de conhecimento (KB)** — definições pré-existentes de tabelas-fonte SAP (bronze) e data
  products (gold OBT) em `knowledge/sap/`, no formato do plugin. A SPEC referencia o que já existe
  na KB e o `run` copia deterministicamente (busca eficiente via `scripts/kb.py find`).

- **Contratos** — toda **tabela** com comentário e chave primária (FK opcional); toda **coluna**
  com comentário e classificação de PII (`nenhum` | `direto` | `indireto` | `sensível`). Metric
  Views com comentário e, por dimensão/medida, comentário e PII. Ingestão sempre **incremental** e
  **idempotente**. Todos os artefatos em **PT-BR**.

- **Fluxo** — atualizar o estado e o código locais, validar contra o Unity Catalog e testar no
  workspace Databricks (Serverless preferencial). Catálogo/schemas nunca são hardcoded: vêm do
  `databricks.yml` (fonte única de configuração).

# data-eng-agent

[Português](README.md) | **English** | [Español](README.es.md)

> Claude Code plugin for **spec-driven development** of data engineering pipelines on Databricks.

Specifies, plans and develops **deterministic** code for the medallion architecture
(bronze → silver → gold), keeping a declarative local state (YAML) that is validated
deterministically against Unity Catalog. Deterministic methods run the tasks whenever
possible; agentic approaches are reserved for the exceptions.

---

## Goals

- **Specify, plan and execute** data model changes through an auditable, incremental cycle.
- **Keep a local source of truth** for the assets (YAML schemas), verifiable against Unity Catalog.
- **Prioritize determinism**: parameterized, reusable notebooks for recurring tasks
  (CDC, SCD Type 1, Metric Views, Genie, Data Classification, Quality Monitor); agentic only for exceptions.
- **Reuse knowledge**: a knowledge base (KB) of SAP source tables and already-modeled data products,
  referenced in the SPEC and copied deterministically at execution time.
- **Governance by contract**: every table and column has a comment and a PII classification; artifacts are written in PT-BR.

---

## Installation

### Prerequisites

- **Claude Code**: A recent version (v2.1.195+ recommended) with plugin and marketplace support.
- **Databricks CLI**: Authenticated (profile in `~/.databrickscfg`) and a SQL warehouse for state validation.
- **Python 3**: With `pyyaml` installed (used by the scripts and notebooks).
- **jq**: Required by `init.sh` (non-destructive permission merge).
- **Git**: Access to the plugin's public GitHub repository.

### Plugin

The plugin is distributed as a **Claude Code marketplace** in the
[`vorodrigues/databricks-data-eng-agent`](https://github.com/vorodrigues/databricks-data-eng-agent)
repository and can be installed directly from GitHub.

**1. Add the marketplace and install the plugin** (inside Claude Code):

```
/plugin marketplace add vorodrigues/databricks-data-eng-agent
/plugin install data-eng-agent@databricks-data-eng-agent
```

**2. Initialize a data project** and follow the workflow:

```
/data-eng-agent:init
```

`init` creates the scaffold (`.data-eng/`, `schemas/`, `resources/`, `src/notebooks/`,
`databricks.yml`) and applies the permissions. Then fill in the `<PREENCHER>` fields in
`databricks.yml` (catalog, schemas per layer, warehouse, host, profile).

---

## Workflow

```
Specify  ->  Plan  ->  Run
```

1. **Use `/specify` to describe the data model change**: writes an incremental SPEC
   of what should change (bronze/silver/gold and transformations). It automatically validates
   the local state against Unity Catalog before specifying and queries the KB to reference
   tables that already exist.

```
/data-eng-agent:specify create the ingestion of the target data model based on the source data model
```

2. **Use `/plan` to generate the phased plan**: derives the phases, tasks and verifiable
   success criteria from the SPEC.

```
/data-eng-agent:plan <optional: spec name>
```

3. **Use `/run` to execute the plan end to end**: takes the ORCHESTRATOR role and
   coordinates the GENERATOR subagent (produces the deliverables) and the EVALUATOR subagent
   (checks each criterion independently), recording the evidence.

```
/data-eng-agent:run <optional: plan name>
```

---

## Skills

| Skill | What it does |
|-------|--------------|
| `init` | Creates the project scaffold and applies the permissions. |
| `validate-state` | Runs `validate_state.py`: deterministic diff of the local state (YAML) × Unity Catalog; reports and asks for conflict resolution. |
| `specify` | Validates the state and writes an incremental SPEC (bronze/silver/gold, ingestion transformations, Metric Views, Genie, governance). Queries the KB and references what already exists. |
| `plan` | Generates a phased plan with tasks and verifiable success criteria. |
| `run` | Executes the plan with the ORCHESTRATOR / GENERATOR / EVALUATOR pattern, recording evidence. |

---

## Standards

- **Layers**
  - **Bronze**: source data model; raw data ingested directly from the originating system.
  - **Silver**: same model as the source, after cleaning (types, trims, dedup, standardization).
  - **Gold**: target, business-oriented model; star schema with SCD Type 1 dimensions and facts,
    and/or OBT/wide tables (denormalized data products). Includes the Metric View.

- **Determinism**: parameterized, reusable notebooks: `ingest_cdc.py` (CDC bronze → silver,
  including silver cleaning), `scd_type1.py` (SCD Type 1 dimension, used by `transform_gold.py`),
  `create_metric_view.py`, `create_genie_space.py`, `enable_data_classification.py` and
  `create_quality_monitor.py`. Exceptions start from a template with minimal changes.

- **Knowledge base (KB)**: pre-existing definitions of SAP source tables (bronze) and data
  products (gold OBT) in `knowledge/sap/`, in the plugin's format. The SPEC references what already
  exists in the KB and `run` copies it deterministically (efficient lookup via `scripts/kb.py find`).

- **Contracts**: every **table** has a comment and a primary key (FK optional); every **column**
  has a comment and a PII classification (`nenhum` (none) | `direto` (direct) | `indireto` (indirect) | `sensível` (sensitive)).
  Metric Views have a comment and, per dimension/measure, a comment and PII. Ingestion is always
  **incremental** and **idempotent**. All artifacts are written in **PT-BR**.

- **Flow**: update the local state and code, validate against Unity Catalog and test in the
  Databricks workspace (Serverless preferred). Catalog/schemas are never hardcoded: they come from
  `databricks.yml` (single source of configuration).

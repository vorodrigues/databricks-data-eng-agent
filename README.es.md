# data-eng-agent

[Português](README.md) | [English](README.en.md) | **Español**

> Plugin de Claude Code para **spec-driven development** de pipelines de ingeniería de datos en Databricks.

Especifica, planifica y desarrolla código **determinístico** para la arquitectura medallion
(bronze → silver → gold), manteniendo un estado local declarativo (YAML) que se valida
de forma determinística contra Unity Catalog. Los métodos determinísticos ejecutan las tareas
siempre que es posible; los enfoques agénticos quedan reservados para las excepciones.

---

## Objetivo

- **Especificar, planificar y ejecutar** cambios en el modelo de datos mediante un ciclo auditable e incremental.
- **Mantener una fuente de verdad local** de los activos (schemas YAML), verificable contra Unity Catalog.
- **Priorizar el determinismo**: notebooks parametrizados y reutilizables para tareas recurrentes
  (CDC, SCD Tipo 1, Metric Views, Genie, Data Classification, Quality Monitor); agéntico solo en las excepciones.
- **Reutilizar conocimiento**: base de conocimiento (KB) de tablas fuente de SAP y data products
  ya modelados, referenciados en la SPEC y copiados de forma determinística en la ejecución.
- **Gobernanza por contrato**: toda tabla y columna con comentario y clasificación de PII; artefactos en PT-BR.

---

## Instalación

### Requisitos previos

- **Claude Code**: Versión reciente (se recomienda v2.1.195+) con soporte de plugins y marketplaces.
- **Databricks CLI**: Autenticada (perfil en `~/.databrickscfg`) y un SQL warehouse para la validación de estado.
- **Python 3**: Con `pyyaml` instalado (usado por los scripts y notebooks).
- **jq**: Necesario para `init.sh` (merge no destructivo de permisos).
- **Git**: Acceso al repositorio público del plugin en GitHub.

### Plugin

El plugin se distribuye como un **marketplace de Claude Code** en el repositorio
[`vorodrigues/databricks-data-eng-agent`](https://github.com/vorodrigues/databricks-data-eng-agent)
y puede instalarse directamente desde GitHub.

**1. Agregue el marketplace e instale el plugin** (dentro de Claude Code):

```
/plugin marketplace add vorodrigues/databricks-data-eng-agent
/plugin install data-eng-agent@databricks-data-eng-agent
```

**2. Inicialice un proyecto de datos** y siga el ciclo de trabajo:

```
/data-eng-agent:init
```

`init` crea el scaffold (`.data-eng/`, `schemas/`, `resources/`, `src/notebooks/`,
`databricks.yml`) y aplica los permisos. Luego, complete los campos `<PREENCHER>` en
`databricks.yml` (catálogo, schemas por capa, warehouse, host, profile).

---

## Ciclo de trabajo

```
Specify  ->  Plan  ->  Run
```

1. **Use `/specify` para describir el cambio en el modelo de datos**: escribe una SPEC
   incremental de lo que debe cambiar (bronze/silver/gold y transformaciones). Valida el estado
   local contra Unity Catalog automáticamente antes de especificar y consulta la KB para
   referenciar tablas ya existentes.

```
/data-eng-agent:specify cree la ingesta del modelo de datos de destino con base en el modelo de datos de origen
```

2. **Use `/plan` para generar el plan por fases**: deriva de la SPEC las fases, tareas y criterios
   de éxito verificables.

```
/data-eng-agent:plan <opcional: nombre de la spec>
```

3. **Use `/run` para ejecutar el plan de punta a punta**: asume el rol de ORCHESTRATOR y
   coordina los subagentes GENERATOR (produce los entregables) y EVALUATOR (verifica cada
   criterio de forma independiente), registrando las evidencias.

```
/data-eng-agent:run <opcional: nombre del plan>
```

---

## Skills

| Skill | Qué hace |
|-------|----------|
| `init` | Crea el scaffold del proyecto y aplica los permisos. |
| `validate-state` | Ejecuta `validate_state.py`: diff determinístico del estado local (YAML) × Unity Catalog; reporta y pide la resolución de conflictos. |
| `specify` | Valida el estado y escribe una SPEC incremental (bronze/silver/gold, transformaciones de ingesta, Metric Views, Genie, gobernanza). Consulta la KB y referencia lo que ya existe. |
| `plan` | Genera un plan por fases con tareas y criterios de éxito verificables. |
| `run` | Ejecuta el plan con el patrón ORCHESTRATOR / GENERATOR / EVALUATOR, registrando evidencias. |

---

## Estándares

- **Capas**
  - **Bronze**: modelo de datos fuente; datos crudos ingeridos directamente del sistema de origen.
  - **Silver**: modelo idéntico a la fuente, después de la limpieza (tipos, trims, dedup, estandarización).
  - **Gold**: modelo destino, orientado al negocio; star schema con dimensiones SCD Tipo 1 y hechos,
    y/o tablas OBT/wide (data products desnormalizados). Incluye la Metric View.

- **Determinismo**: notebooks parametrizados y reutilizables: `ingest_cdc.py` (CDC bronze → silver,
  con la limpieza de la silver), `scd_type1.py` (dimensión SCD Tipo 1, consumido por `transform_gold.py`),
  `create_metric_view.py`, `create_genie_space.py`, `enable_data_classification.py` y
  `create_quality_monitor.py`. Las excepciones parten de un template con cambios mínimos.

- **Base de conocimiento (KB)**: definiciones preexistentes de tablas fuente de SAP (bronze) y data
  products (gold OBT) en `knowledge/sap/`, en el formato del plugin. La SPEC referencia lo que ya existe
  en la KB y `run` lo copia de forma determinística (búsqueda eficiente vía `scripts/kb.py find`).

- **Contratos**: toda **tabla** con comentario y clave primaria (FK opcional); toda **columna**
  con comentario y clasificación de PII (`nenhum` (ninguno) | `direto` (directo) | `indireto` (indirecto) | `sensível` (sensible)).
  Metric Views con comentario y, por dimensión/medida, comentario y PII. Ingesta siempre **incremental** e
  **idempotente**. Todos los artefactos en **PT-BR**.

- **Flujo**: actualizar el estado y el código locales, validar contra Unity Catalog y probar en el
  workspace de Databricks (Serverless preferente). Catálogo/schemas nunca se hardcodean: vienen de
  `databricks.yml` (fuente única de configuración).

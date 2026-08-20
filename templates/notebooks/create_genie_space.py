# Databricks notebook source
# MAGIC %md
# MAGIC # Genie Space — criacao deterministica
# MAGIC
# MAGIC Notebook **parametrizado**, dirigido pelo **estado do Genie space**
# MAGIC (`schemas/genie/<nome>.yaml`). O YAML e a fonte de verdade: dele saem o titulo, a
# MAGIC descricao, as tabelas/metric views expostas, as instrucoes e as perguntas de exemplo.
# MAGIC Usa o Databricks SDK: `w.genie.create_space(...)`.
# MAGIC
# MAGIC SDK: https://databricks-sdk-py.readthedocs.io/en/latest/workspace/dashboards/genie.html
# MAGIC
# MAGIC Idempotente por reexecucao: procura um space com o mesmo titulo e faz `update_space`;
# MAGIC caso nao exista, `create_space`.

# COMMAND ----------
dbutils.widgets.text("catalogo", "")
dbutils.widgets.text("schema_destino", "")     # schema UC das tabelas/metric views (gold)
dbutils.widgets.text("warehouse_id", "")       # SQL warehouse (Pro/Serverless) do Genie
dbutils.widgets.text("caminho_estado", "")     # path do YAML de estado do Genie space

catalogo = dbutils.widgets.get("catalogo")
schema_destino = dbutils.widgets.get("schema_destino")
warehouse_id = dbutils.widgets.get("warehouse_id")
caminho_estado = dbutils.widgets.get("caminho_estado")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Estado (YAML do Genie space)

# COMMAND ----------
import json
import yaml
from databricks.sdk import WorkspaceClient

with open(caminho_estado) as f:
    estado = yaml.safe_load(f)

titulo = estado["titulo"]
descricao = (estado.get("descricao") or "").strip()
tabelas = [f"{catalogo}.{schema_destino}.{t.split('.')[-1]}" for t in (estado.get("tabelas") or [])]
instrucoes = estado.get("instrucoes") or []
perguntas = estado.get("perguntas_exemplo") or []

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Monta o serialized_space e cria/atualiza (idempotente por titulo)

# COMMAND ----------
serialized = json.dumps(
    {
        "version": 1,
        "tables": [{"full_name": t} for t in tabelas],
        "instructions": "\n".join(instrucoes),
        "sample_questions": perguntas,
    }
)

w = WorkspaceClient()

existente = next((s for s in w.genie.list_spaces() if getattr(s, "title", None) == titulo), None)
if existente is not None:
    space = w.genie.update_space(
        space_id=existente.space_id,
        title=titulo,
        description=descricao,
        warehouse_id=warehouse_id,
        serialized_space=serialized,
    )
    print(f"OK: Genie space atualizado ({space.space_id}).")
else:
    space = w.genie.create_space(
        warehouse_id=warehouse_id,
        serialized_space=serialized,
        title=titulo,
        description=descricao,
    )
    print(f"OK: Genie space criado ({space.space_id}).")

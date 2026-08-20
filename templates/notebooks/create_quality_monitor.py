# Databricks notebook source
# MAGIC %md
# MAGIC # Quality Monitor — criacao deterministica
# MAGIC
# MAGIC Notebook **parametrizado**, dirigido pelo **estado do monitor**
# MAGIC (`schemas/governanca/<nome>.yaml`). Cria um Quality Monitor v2 sobre um schema ou
# MAGIC tabela via SDK: `w.quality_monitor_v2`. O UUID do objeto e resolvido a partir do nome.
# MAGIC
# MAGIC SDK: https://databricks-sdk-py.readthedocs.io/en/latest/workspace/qualitymonitorv2/quality_monitor_v2.html
# MAGIC
# MAGIC Idempotente: se ja existe monitor para o objeto, confirma; senao, cria.

# COMMAND ----------
dbutils.widgets.text("catalogo", "")            # catalogo alvo
dbutils.widgets.text("caminho_estado", "")      # path do YAML de estado do monitor

catalogo = dbutils.widgets.get("catalogo")
caminho_estado = dbutils.widgets.get("caminho_estado")

# COMMAND ----------
import yaml
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.qualitymonitorv2 import QualityMonitor

with open(caminho_estado) as f:
    estado = yaml.safe_load(f)

objeto_tipo = estado.get("objeto_tipo", "schema")     # schema | table
objeto_nome = estado["objeto_nome"].split(".")[-1]    # nome curto (schema ou tabela)

w = WorkspaceClient()

# Resolve o UUID do securable a partir do nome completo.
if objeto_tipo == "schema":
    full = f"{catalogo}.{objeto_nome}"
    object_id = w.schemas.get(full).schema_id
else:
    # tabela: 'schema.tabela' no objeto_nome do estado
    full = f"{catalogo}.{estado['objeto_nome']}"
    object_id = w.tables.get(full).table_id

# COMMAND ----------
monitor = QualityMonitor(object_type=objeto_tipo, object_id=object_id)
try:
    criado = w.quality_monitor_v2.create_quality_monitor(monitor)
    print(f"OK: quality monitor criado para {full} ({object_id}).")
except Exception as e:
    print(f"Monitor ja existente ou erro tratado para {full}: {e}")

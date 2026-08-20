# Databricks notebook source
# MAGIC %md
# MAGIC # Data Classification — ativacao deterministica
# MAGIC
# MAGIC Notebook **parametrizado**, dirigido pelo **estado da config**
# MAGIC (`schemas/governanca/data_classification.yaml`). Ativa a deteccao automatica de dados
# MAGIC sensiveis (PII) no catalogo do projeto via SDK: `w.data_classification`.
# MAGIC
# MAGIC SDK: https://databricks-sdk-py.readthedocs.io/en/latest/workspace/dataclassification/data_classification.html
# MAGIC
# MAGIC Idempotente: se a config do catalogo ja existe, apenas confirma; senao, cria.

# COMMAND ----------
dbutils.widgets.text("catalogo", "")            # catalogo alvo
dbutils.widgets.text("caminho_estado", "")      # path do YAML de estado (opcional)

catalogo = dbutils.widgets.get("catalogo")

# COMMAND ----------
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dataclassification import CatalogConfig

w = WorkspaceClient()
nome = f"catalogs/{catalogo}/config"

try:
    cfg = w.data_classification.get_catalog_config(name=nome)
    print(f"OK: data classification ja configurada para {catalogo}.")
except Exception:
    cfg = w.data_classification.create_catalog_config(
        parent=f"catalogs/{catalogo}",
        catalog_config=CatalogConfig(),
    )
    print(f"OK: data classification ativada para {catalogo}.")

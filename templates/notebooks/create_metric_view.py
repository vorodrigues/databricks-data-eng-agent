# Databricks notebook source
# MAGIC %md
# MAGIC # Metric View — criacao deterministica
# MAGIC
# MAGIC Notebook **parametrizado**, dirigido pelo **estado da metric view**
# MAGIC (`schemas/metric_views/<nome>.yaml`). O YAML e a fonte de verdade: dele saem a source,
# MAGIC os joins, as dimensoes e as medidas. O notebook monta a spec YAML de metric view da
# MAGIC Databricks e emite `CREATE OR REPLACE VIEW ... WITH METRICS LANGUAGE YAML`.
# MAGIC
# MAGIC Idempotente (CREATE OR REPLACE). Referencia da spec:
# MAGIC https://docs.databricks.com/aws/en/uc-semantics/metric-views/yaml-reference

# COMMAND ----------
dbutils.widgets.text("catalogo", "")
dbutils.widgets.text("schema_destino", "")     # schema UC onde a metric view sera criada (gold)
dbutils.widgets.text("caminho_estado", "")     # path do YAML de estado da metric view

catalogo = dbutils.widgets.get("catalogo")
schema_destino = dbutils.widgets.get("schema_destino")
caminho_estado = dbutils.widgets.get("caminho_estado")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Estado (YAML da metric view)

# COMMAND ----------
import yaml

with open(caminho_estado) as f:
    estado = yaml.safe_load(f)

nome = estado["tabela"]
comentario = (estado.get("comentario") or "").strip()
versao = str(estado.get("versao_spec", "0.1"))
fonte = estado["fonte"].split(".")[-1]                 # tabela de origem (na gold)
source_fqn = f"{catalogo}.{schema_destino}.{fonte}"
destino = f"{catalogo}.{schema_destino}.{nome}"

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Monta a spec YAML da metric view a partir do estado

# COMMAND ----------
def _fqn(ref):
    # 'gold.dim_cliente' -> 'catalogo.schema_destino.dim_cliente'
    return f"{catalogo}.{schema_destino}.{ref.split('.')[-1]}"


spec = {
    "version": versao,
    "source": source_fqn,
}
if comentario:
    spec["comment"] = comentario

joins = estado.get("joins") or []
if joins:
    spec["joins"] = [
        {
            "name": j["nome"],
            "source": _fqn(j["fonte"]),
            "on": j["on"],
            "cardinality": j.get("cardinalidade", "many_to_one"),
        }
        for j in joins
    ]

spec["dimensions"] = [
    {"name": d["nome"], "expr": d["expr"], **({"comment": d["comentario"]} if d.get("comentario") else {})}
    for d in (estado.get("dimensoes") or [])
]
spec["measures"] = [
    {"name": m["nome"], "expr": m["expr"], **({"comment": m["comentario"]} if m.get("comentario") else {})}
    for m in (estado.get("medidas") or [])
]

spec_yaml = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
print(spec_yaml)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Cria a metric view (idempotente)

# COMMAND ----------
ddl = f"CREATE OR REPLACE VIEW {destino} WITH METRICS LANGUAGE YAML AS $$\n{spec_yaml}$$"
spark.sql(ddl)
if comentario:
    spark.sql(f"COMMENT ON VIEW {destino} IS '{comentario.replace(chr(39), chr(39)*2)}'")

print(f"OK: metric view {destino} criada.")

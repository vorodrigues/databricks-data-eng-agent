# Databricks notebook source
# MAGIC %md
# MAGIC # Ingestao CDC — bronze -> silver
# MAGIC
# MAGIC Notebook **parametrizado, incremental e idempotente**, dirigido pelo **estado da silver**
# MAGIC (`schemas/silver/<tabela>.yaml`). O YAML e a fonte de verdade: dele saem a projecao das
# MAGIC colunas (com renomeacao `origem -> nome`), a chave do `MERGE`, a coluna de watermark e o
# MAGIC comentario da tabela. Assim o mesmo notebook atende todas as silvers sem editar codigo.
# MAGIC
# MAGIC Le apenas registros novos (por watermark), projeta/renomeia conforme o YAML, aplica a
# MAGIC limpeza da silver e faz `MERGE` pela chave. Reexecutar nao duplica.

# COMMAND ----------
dbutils.widgets.text("catalogo", "")
dbutils.widgets.text("schema_origem", "")      # schema UC da bronze
dbutils.widgets.text("schema_destino", "")     # schema UC da silver
dbutils.widgets.text("caminho_estado", "")     # path do YAML de estado da silver

catalogo = dbutils.widgets.get("catalogo")
schema_origem = dbutils.widgets.get("schema_origem")
schema_destino = dbutils.widgets.get("schema_destino")
caminho_estado = dbutils.widgets.get("caminho_estado")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Estado (YAML da silver)
# MAGIC Carrega o contrato da tabela e deriva projecao, chaves, watermark e comentario.

# COMMAND ----------
import yaml

with open(caminho_estado) as f:
    estado = yaml.safe_load(f)

tabela_destino = estado["tabela"]
tabela_origem = estado["fonte"].split(".")[-1]        # ex.: "bronze.kna1" -> "kna1"
chaves = list(estado["chave_primaria"])
comentario_tabela = (estado.get("comentario") or "").strip()
wm_destino = estado.get("watermark")                  # nome da coluna de watermark na silver

# mapa nome_silver -> nome_origem (origem ausente => mesmo nome)
mapa = {c["nome"]: c.get("origem", c["nome"]) for c in estado["colunas"]}
wm_origem = mapa.get(wm_destino) if wm_destino else None

origem = f"{catalogo}.{schema_origem}.{tabela_origem}"
destino = f"{catalogo}.{schema_destino}.{tabela_destino}"
assert chaves, "o YAML de estado precisa definir chave_primaria"

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Watermark incremental
# MAGIC Le da origem somente o que e mais novo que o maximo ja carregado no destino.

# COMMAND ----------
from delta.tables import DeltaTable
from pyspark.sql import functions as F, Window

destino_existe = spark.catalog.tableExists(destino)
ultimo_wm = None
if destino_existe and wm_destino:
    ultimo_wm = spark.table(destino).agg(F.max(wm_destino)).collect()[0][0]

df = spark.table(origem)
if ultimo_wm is not None and wm_origem:
    df = df.filter(F.col(wm_origem) > F.lit(ultimo_wm))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Projecao + renomeacao (dirigida pelo YAML)
# MAGIC Seleciona apenas as colunas modeladas na silver, aplicando `origem -> nome`.

# COMMAND ----------
df = df.select(*[F.col(orig).alias(nome) for nome, orig in mapa.items()])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Limpeza (camada silver)
# MAGIC Limpeza/padronizacao sobre as colunas ja renomeadas. Ajuste o minimo necessario.

# COMMAND ----------
def limpar(df):
    # Exemplo: normaliza espacos em colunas string.
    for campo in df.schema.fields:
        if campo.dataType.simpleString() == "string":
            df = df.withColumn(campo.name, F.trim(F.col(campo.name)))
    # Dedup: mantem a versao mais recente por chave (idempotencia no lote).
    if wm_destino:
        w = Window.partitionBy(*chaves).orderBy(F.col(wm_destino).desc())
        df = df.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")
    return df


df = limpar(df)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Materializacao idempotente (MERGE)
# MAGIC Cria o destino na primeira execucao e faz upsert pela chave nas seguintes.

# COMMAND ----------
if not destino_existe:
    df.limit(0).write.format("delta").saveAsTable(destino)
    if comentario_tabela:
        spark.sql(f"COMMENT ON TABLE {destino} IS '{comentario_tabela.replace(chr(39), chr(39)*2)}'")

cond = " AND ".join([f"d.{k} = o.{k}" for k in chaves])
(
    DeltaTable.forName(spark, destino).alias("d")
    .merge(df.alias("o"), cond)
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

print(f"OK: {destino} atualizado a partir de {origem} (linhas do lote: {df.count()})")

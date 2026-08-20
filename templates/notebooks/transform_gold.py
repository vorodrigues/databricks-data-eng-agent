# Databricks notebook source
# MAGIC %md
# MAGIC # Transformacao — silver -> gold
# MAGIC
# MAGIC Notebook **parametrizado**, dirigido pelo **estado da gold** (`schemas/gold/<tabela>.yaml`).
# MAGIC O YAML e a fonte de verdade: dele saem a projecao das colunas com `origem` (vindas da
# MAGIC silver), a entidade (dimensao/fato), as chaves, a chave surrogada, o watermark e o
# MAGIC comentario.
# MAGIC
# MAGIC Divisao de responsabilidades:
# MAGIC - **Declarativo (YAML)**: colunas com `origem` sao projetadas automaticamente da silver.
# MAGIC - **Gerado**: a chave surrogada e criada pelo `scd_type1`; `_atualizado_em` idem.
# MAGIC - **Excecao (codigo)**: colunas sem `origem` (metricas/derivadas) sao produzidas na
# MAGIC   funcao `transformar` — joins, agregacoes e metricas de negocio. Alteracao minima.

# COMMAND ----------
# MAGIC %run ../notebooks/scd_type1

# COMMAND ----------
dbutils.widgets.text("catalogo", "")
dbutils.widgets.text("schema_origem", "")      # schema UC da silver
dbutils.widgets.text("schema_destino", "")     # schema UC da gold
dbutils.widgets.text("caminho_estado", "")     # path do YAML de estado da gold

catalogo = dbutils.widgets.get("catalogo")
schema_origem = dbutils.widgets.get("schema_origem")
schema_destino = dbutils.widgets.get("schema_destino")
caminho_estado = dbutils.widgets.get("caminho_estado")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Estado (YAML da gold)

# COMMAND ----------
import yaml
from pyspark.sql import functions as F
from delta.tables import DeltaTable

with open(caminho_estado) as f:
    estado = yaml.safe_load(f)

tabela_destino = estado["tabela"]
fonte_tabela = estado["fonte"].split(".")[-1]
entidade = estado.get("entidade", "dimensao")            # dimensao | fato
comentario_tabela = (estado.get("comentario") or "").strip()
chave_negocio = list(estado.get("chave_negocio", []) or [])
chave_surrogada = estado.get("chave_surrogada")
chave_primaria = list(estado.get("chave_primaria", []) or [])
wm_destino = estado.get("watermark")

# colunas com 'origem' sao projetadas da silver; as demais (sk, metricas) sao geradas
proj = {c["nome"]: c["origem"] for c in estado["colunas"] if "origem" in c}
wm_origem = proj.get(wm_destino) if wm_destino else None

fonte = f"{catalogo}.{schema_origem}.{fonte_tabela}"
destino = f"{catalogo}.{schema_destino}.{tabela_destino}"

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Projecao da silver + incremental opcional

# COMMAND ----------
destino_existe = spark.catalog.tableExists(destino)
ultimo_wm = None
if destino_existe and wm_destino:
    ultimo_wm = spark.table(destino).agg(F.max(wm_destino)).collect()[0][0]

base = spark.table(fonte)
if ultimo_wm is not None and wm_origem:
    base = base.filter(F.col(wm_origem) > F.lit(ultimo_wm))
if proj:
    base = base.select(*[F.col(orig).alias(nome) for nome, orig in proj.items()])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Logica de negocio (excecao)
# MAGIC Produza aqui as colunas sem `origem` (agregacoes, metricas, joins). Sem alteracoes,
# MAGIC materializa a projecao direta da silver.

# COMMAND ----------
def transformar(df):
    # Ex.: df = df.join(...).groupBy(*chave_negocio).agg(F.sum(...).alias("metrica"))
    return df


df = transformar(base)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Materializacao
# MAGIC Dimensao -> SCD Tipo 1 (gera a chave surrogada). Fato -> MERGE incremental pela PK.
# MAGIC OBT (tabela larga denormalizada) -> MERGE pela PK se houver; senao, overwrite idempotente.

# COMMAND ----------
def _cria_vazia_com_comentario():
    df.limit(0).write.format("delta").mode("overwrite").saveAsTable(destino)
    if comentario_tabela:
        spark.sql(f"COMMENT ON TABLE {destino} IS '{comentario_tabela.replace(chr(39), chr(39)*2)}'")


if entidade == "dimensao":
    colunas_atributo = [c for c in df.columns if c not in chave_negocio and c != chave_surrogada]
    aplicar_scd_tipo1(
        spark,
        df_origem=df,
        tabela_destino=destino,
        chave_negocio=chave_negocio,
        coluna_sk=chave_surrogada,
        colunas_atributo=colunas_atributo,
        comentario_tabela=comentario_tabela,
    )
elif entidade == "obt" and not chave_primaria:
    # OBT sem PK declarada: overwrite completo (idempotente). Preferivel definir a PK
    # do produto para permitir MERGE incremental — ver revisao dos data products.
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(destino)
    if comentario_tabela:
        spark.sql(f"COMMENT ON TABLE {destino} IS '{comentario_tabela.replace(chr(39), chr(39)*2)}'")
else:
    # fato ou OBT com PK: MERGE incremental idempotente pela chave primaria.
    if not chave_primaria:
        raise ValueError(f"{destino}: entidade '{entidade}' exige chave_primaria para o MERGE.")
    if not destino_existe:
        _cria_vazia_com_comentario()
    cond = " AND ".join([f"d.{k} = o.{k}" for k in chave_primaria])
    (
        DeltaTable.forName(spark, destino).alias("d")
        .merge(df.alias("o"), cond)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

print(f"OK: {destino} materializada ({entidade}).")

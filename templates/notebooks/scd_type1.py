# Databricks notebook source
# MAGIC %md
# MAGIC # Modulo deterministico — SCD Tipo 1
# MAGIC
# MAGIC Codigo reutilizavel (sem widgets, sem efeitos colaterais) para materializar dimensoes
# MAGIC **SCD Tipo 1**: sobrescreve os atributos do registro corrente pela chave de negocio,
# MAGIC preservando a chave surrogada existente e gerando novas para chaves ineditas.
# MAGIC
# MAGIC Consumido pelos notebooks de gold via `%run ../notebooks/scd_type1`. Idempotente:
# MAGIC reprocessar a mesma origem nao altera chaves surrogadas nem duplica linhas.

# COMMAND ----------
from delta.tables import DeltaTable
from pyspark.sql import functions as F, Window


def aplicar_scd_tipo1(
    spark,
    df_origem,
    tabela_destino,
    chave_negocio,
    coluna_sk,
    colunas_atributo,
    comentario_tabela="",
    coluna_auditoria="_atualizado_em",
):
    """Materializa uma dimensao SCD Tipo 1.

    df_origem        : DataFrame ja transformado (1 linha por chave de negocio).
    tabela_destino   : nome completo catalogo.schema.tabela.
    chave_negocio    : lista de colunas da chave natural.
    coluna_sk        : nome da coluna de chave surrogada.
    colunas_atributo : colunas sobrescritas no match (atributos Tipo 1).
    """
    df = df_origem
    if coluna_auditoria:
        df = df.withColumn(coluna_auditoria, F.current_timestamp())

    destino_existe = spark.catalog.tableExists(tabela_destino)
    if not destino_existe:
        # Cria o destino com surrogate keys sequenciais a partir de 1.
        w = Window.orderBy(*chave_negocio)
        inicial = df.withColumn(coluna_sk, F.row_number().over(w).cast("bigint"))
        inicial.write.format("delta").saveAsTable(tabela_destino)
        if comentario_tabela:
            spark.sql(f"COMMENT ON TABLE {tabela_destino} IS '{comentario_tabela.replace(chr(39), chr(39)*2)}'")
        return

    destino = DeltaTable.forName(spark, tabela_destino)
    max_sk = spark.table(tabela_destino).agg(F.coalesce(F.max(coluna_sk), F.lit(0))).collect()[0][0]

    # Novas chaves de negocio recebem surrogate keys apos o maior existente.
    existentes = spark.table(tabela_destino).select(*chave_negocio).distinct()
    novos = df.join(existentes, on=chave_negocio, how="left_anti")
    w = Window.orderBy(*chave_negocio)
    novos = novos.withColumn(coluna_sk, (F.lit(max_sk) + F.row_number().over(w)).cast("bigint"))
    conhecidos = df.join(existentes, on=chave_negocio, how="left_semi").withColumn(coluna_sk, F.lit(None).cast("bigint"))
    df_final = novos.unionByName(conhecidos)

    cond = " AND ".join([f"d.{k} = o.{k}" for k in chave_negocio])
    update_set = {c: f"o.{c}" for c in colunas_atributo}
    if coluna_auditoria:
        update_set[coluna_auditoria] = f"o.{coluna_auditoria}"

    (
        destino.alias("d")
        .merge(df_final.alias("o"), cond)
        .whenMatchedUpdate(set=update_set)   # Tipo 1: sobrescreve atributos, mantem a SK
        .whenNotMatchedInsertAll()
        .execute()
    )

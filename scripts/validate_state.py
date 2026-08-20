#!/usr/bin/env python3
"""Valida deterministicamente o estado local (YAML) contra o Unity Catalog.

Le as definicoes locais em schemas/<camada>/*.yaml, consulta o information_schema
do catalogo via Statement Execution API (Databricks CLI) e reporta todos os diffs
por categoria: tabelas, colunas, tipos, comentarios, nulabilidade, chaves e PII.

Saida: relatorio em texto. Codigo de saida 0 quando nao ha diff, 1 quando ha.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("erro: PyYAML nao encontrado. Instale com: pip install pyyaml")

LAYERS = ("bronze", "silver", "gold")


# --------------------------------------------------------------------------- #
# Configuracao
# --------------------------------------------------------------------------- #
def load_config(bundle_path: Path, args) -> dict:
    """Le a config a partir do databricks.yml (fonte unica de verdade).

    Resolve os valores das `variables` do bundle, aplicando override do `target`
    escolhido (default: target marcado `default: true`, senao `dev`).
    """
    if not bundle_path.exists():
        sys.exit(f"erro: {bundle_path} nao encontrado (rode a skill init na raiz do projeto)")
    b = yaml.safe_load(bundle_path.read_text()) or {}
    variables = b.get("variables", {}) or {}
    targets = b.get("targets", {}) or {}

    tname = args.target or next(
        (k for k, v in targets.items() if isinstance(v, dict) and v.get("default")), None
    ) or ("dev" if "dev" in targets else next(iter(targets), None))
    target = targets.get(tname, {}) if tname else {}
    tvars = target.get("variables", {}) or {}

    def unwrap(v):
        return v.get("default") if isinstance(v, dict) else v

    def var(name, default=None):
        if name in tvars:
            return unwrap(tvars[name])
        if name in variables:
            return unwrap(variables[name])
        return default

    resolved = {
        # auth e local: flag > env DATABRICKS_CONFIG_PROFILE > (deixa a CLI resolver)
        "profile": args.profile or os.environ.get("DATABRICKS_CONFIG_PROFILE"),
        "warehouse_id": args.warehouse_id or var("warehouse_id", ""),
        "catalog": args.catalog or var("catalog", ""),
        "schemas": {
            "bronze": var("schema_bronze", "bronze"),
            "silver": var("schema_silver", "silver"),
            "gold": var("schema_gold", "gold"),
        },
        "schemas_dir": args.schemas_dir or "schemas",
        "pii_tag": args.pii_tag or "pii",
    }
    missing = [k for k in ("warehouse_id", "catalog") if not resolved[k]]
    if missing or "<PREENCHER>" in (str(resolved["catalog"]), str(resolved["warehouse_id"])):
        sys.exit(f"erro: preencha {', '.join(missing) or 'catalog/warehouse_id'} em {bundle_path} (target: {tname}) ou via flags")
    return resolved


# --------------------------------------------------------------------------- #
# Estado local
# --------------------------------------------------------------------------- #
def norm_type(t: str) -> str:
    return "".join(str(t).lower().split())


def load_local(schemas_dir: Path) -> dict:
    """Retorna {(camada, tabela): definicao normalizada}."""
    model = {}
    for layer in LAYERS:
        layer_dir = schemas_dir / layer
        if not layer_dir.is_dir():
            continue
        for f in sorted(layer_dir.glob("*.yaml")):
            spec = yaml.safe_load(f.read_text()) or {}
            tabela = spec.get("tabela") or f.stem
            cols = {}
            for c in spec.get("colunas", []) or []:
                cols[c["nome"]] = {
                    "tipo": norm_type(c.get("tipo", "")),
                    "comentario": (c.get("comentario") or "").strip(),
                    "pii": (c.get("pii") or "nenhum").strip().lower(),
                    "nulo": bool(c.get("nulo", True)),
                }
            model[(layer, tabela)] = {
                "arquivo": str(f),
                "comentario": (spec.get("comentario") or "").strip(),
                "chave_primaria": list(spec.get("chave_primaria", []) or []),
                "chaves_estrangeiras": [
                    col for fk in (spec.get("chaves_estrangeiras", []) or [])
                    for col in fk.get("colunas", [])
                ],
                "colunas": cols,
            }
    return model


# --------------------------------------------------------------------------- #
# Estado remoto (Unity Catalog)
# --------------------------------------------------------------------------- #
def run_sql(profile: str, warehouse_id: str, catalog: str, statement: str) -> list[list]:
    body = {
        "warehouse_id": warehouse_id,
        "catalog": catalog,
        "statement": statement,
        "wait_timeout": "30s",
        "disposition": "INLINE",
        "format": "JSON_ARRAY",
    }
    out = _api("post", "/api/2.0/sql/statements", profile, body)
    state = out.get("status", {}).get("state")
    stmt_id = out.get("statement_id")
    while state in ("PENDING", "RUNNING"):
        time.sleep(1)
        out = _api("get", f"/api/2.0/sql/statements/{stmt_id}", profile)
        state = out.get("status", {}).get("state")
    if state != "SUCCEEDED":
        err = out.get("status", {}).get("error", {}).get("message", state)
        sys.exit(f"erro na consulta ao Unity Catalog: {err}")
    return out.get("result", {}).get("data_array", []) or []


def _api(method: str, path: str, profile: str, body: dict | None = None) -> dict:
    cmd = ["databricks", "api", method, path]
    if profile:                       # sem profile explicito, a CLI resolve (env/DEFAULT/host)
        cmd += ["--profile", profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"erro na Databricks CLI: {proc.stderr.strip() or proc.stdout.strip()}")
    return json.loads(proc.stdout or "{}")


def in_list(values) -> str:
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def load_remote(cfg: dict, schema_set: set[str]) -> dict:
    """Retorna {(schema, tabela): definicao} para os schemas informados."""
    catalog, profile, wh = cfg["catalog"], cfg["profile"], cfg["warehouse_id"]
    if not schema_set:
        return {}
    schemas_sql = in_list(sorted(schema_set))

    tables = {}

    def get(schema, table):
        return tables.setdefault(
            (schema, table),
            {"comentario": "", "colunas": {}, "chave_primaria": [], "chaves_estrangeiras": []},
        )

    for s, t, comment in run_sql(profile, wh, catalog, f"""
        SELECT table_schema, table_name, comment
        FROM {catalog}.information_schema.tables
        WHERE table_schema IN ({schemas_sql})"""):
        get(s, t)["comentario"] = (comment or "").strip()

    for s, t, col, dtype, comment, nullable in run_sql(profile, wh, catalog, f"""
        SELECT table_schema, table_name, column_name, full_data_type, comment, is_nullable
        FROM {catalog}.information_schema.columns
        WHERE table_schema IN ({schemas_sql})"""):
        get(s, t)["colunas"][col] = {
            "tipo": norm_type(dtype),
            "comentario": (comment or "").strip(),
            "pii": "nenhum",
            "nulo": str(nullable).upper() != "NO",
        }

    for s, t, ctype, col, _pos in run_sql(profile, wh, catalog, f"""
        SELECT tc.table_schema, tc.table_name, tc.constraint_type,
               kcu.column_name, kcu.ordinal_position
        FROM {catalog}.information_schema.table_constraints tc
        JOIN {catalog}.information_schema.key_column_usage kcu
          ON tc.constraint_catalog = kcu.constraint_catalog
         AND tc.constraint_schema  = kcu.constraint_schema
         AND tc.constraint_name    = kcu.constraint_name
        WHERE tc.table_schema IN ({schemas_sql})
          AND tc.constraint_type IN ('PRIMARY KEY','FOREIGN KEY')
        ORDER BY kcu.ordinal_position"""):
        rec = get(s, t)
        key = "chave_primaria" if ctype == "PRIMARY KEY" else "chaves_estrangeiras"
        rec[key].append(col)

    for s, t, col, _tag, val in run_sql(profile, wh, catalog, f"""
        SELECT schema_name, table_name, column_name, tag_name, tag_value
        FROM {catalog}.information_schema.column_tags
        WHERE schema_name IN ({schemas_sql}) AND tag_name = '{cfg["pii_tag"]}'"""):
        rec = get(s, t)
        if col in rec["colunas"]:
            rec["colunas"][col]["pii"] = (val or "").strip().lower() or "nenhum"

    return tables


# --------------------------------------------------------------------------- #
# Diff
# --------------------------------------------------------------------------- #
def diff(local: dict, remote: dict, cfg: dict) -> list[str]:
    diffs = []
    layer_of_schema = {cfg["schemas"][l]: l for l in LAYERS}

    def loc(layer, tabela):
        return f"{cfg['schemas'][layer]}.{tabela} [{layer}]"

    local_schema_tables = {(cfg["schemas"][l], t) for (l, t) in local}

    # tabelas ausentes no UC
    for (layer, tabela), ldef in sorted(local.items()):
        schema = cfg["schemas"][layer]
        if (schema, tabela) not in remote:
            diffs.append(f"[TABELA AUSENTE NO UC] {loc(layer, tabela)} definida em {ldef['arquivo']}")

    # tabelas somente no UC (dentro dos schemas modelados)
    for (schema, tabela) in sorted(remote):
        if (schema, tabela) not in local_schema_tables:
            layer = layer_of_schema.get(schema, schema)
            diffs.append(f"[TABELA SOMENTE NO UC] {schema}.{tabela} [{layer}] sem definicao local")

    # diffs por tabela presente em ambos
    for (layer, tabela), ldef in sorted(local.items()):
        schema = cfg["schemas"][layer]
        rdef = remote.get((schema, tabela))
        if rdef is None:
            continue
        ref = loc(layer, tabela)

        if ldef["comentario"] != rdef["comentario"]:
            diffs.append(f"[COMENTARIO TABELA] {ref}: local={ldef['comentario']!r} UC={rdef['comentario']!r}")

        if sorted(ldef["chave_primaria"]) != sorted(rdef["chave_primaria"]):
            diffs.append(f"[CHAVE PRIMARIA] {ref}: local={ldef['chave_primaria']} UC={rdef['chave_primaria']}")

        if sorted(ldef["chaves_estrangeiras"]) != sorted(rdef["chaves_estrangeiras"]):
            diffs.append(f"[CHAVE ESTRANGEIRA] {ref}: local={sorted(ldef['chaves_estrangeiras'])} UC={sorted(rdef['chaves_estrangeiras'])}")

        lcols, rcols = ldef["colunas"], rdef["colunas"]
        for col in lcols:
            if col not in rcols:
                diffs.append(f"[COLUNA AUSENTE NO UC] {ref}.{col}")
        for col in rcols:
            if col not in lcols:
                diffs.append(f"[COLUNA SOMENTE NO UC] {ref}.{col}")
        for col in lcols:
            if col not in rcols:
                continue
            lc, rc = lcols[col], rcols[col]
            if lc["tipo"] != rc["tipo"]:
                diffs.append(f"[TIPO] {ref}.{col}: local={lc['tipo']} UC={rc['tipo']}")
            if lc["comentario"] != rc["comentario"]:
                diffs.append(f"[COMENTARIO COLUNA] {ref}.{col}: local={lc['comentario']!r} UC={rc['comentario']!r}")
            if lc["nulo"] != rc["nulo"]:
                diffs.append(f"[NULABILIDADE] {ref}.{col}: local nulo={lc['nulo']} UC nulo={rc['nulo']}")
            if lc["pii"] != rc["pii"]:
                diffs.append(f"[PII] {ref}.{col}: local={lc['pii']} UC={rc['pii']}")

    return diffs


# --------------------------------------------------------------------------- #
def main() -> int:
    p = argparse.ArgumentParser(description="Valida estado local (YAML) x Unity Catalog.")
    p.add_argument("--bundle", default="databricks.yml", help="caminho do databricks.yml (fonte de config)")
    p.add_argument("--target", help="target do bundle (default: o marcado default:true, senao dev)")
    p.add_argument("--schemas-dir")
    p.add_argument("--catalog")
    p.add_argument("--profile")
    p.add_argument("--warehouse-id")
    p.add_argument("--pii-tag")
    p.add_argument("--layer", choices=LAYERS, help="valida apenas uma camada")
    args = p.parse_args()

    cfg = load_config(Path(args.bundle), args)
    local = load_local(Path(cfg["schemas_dir"]))
    if args.layer:
        local = {(l, t): v for (l, t), v in local.items() if l == args.layer}
    if not local:
        print("nenhuma definicao local encontrada em", cfg["schemas_dir"])
        return 0

    schema_set = {cfg["schemas"][l] for (l, _t) in local}
    remote = load_remote(cfg, schema_set)
    diffs = diff(local, remote, cfg)

    print(f"catalogo: {cfg['catalog']} | schemas: {sorted(schema_set)} | tabelas locais: {len(local)}")
    if not diffs:
        print("\nSEM DIFF — estado local e Unity Catalog estao sincronizados.")
        return 0
    print(f"\nDIFF ENCONTRADO — {len(diffs)} divergencia(s):\n")
    for d in diffs:
        print("  -", d)
    print("\nResolva os conflitos acima antes de prosseguir.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

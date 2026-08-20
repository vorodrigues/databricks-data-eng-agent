#!/usr/bin/env python3
"""kb.py — base de conhecimento (KB) de tabelas-fonte SAP e data products.

Entrada unica para operar a KB do plugin, que vive em
`${CLAUDE_PLUGIN_ROOT}/knowledge/sap/{bronze,gold}/<tabela>.yaml` no formato do
plugin (mesmo schema de `schemas/`). Subcomandos:

    import   Gera os esqueletos da KB a partir das anotacoes do projeto Cortex
             (mapeamento MECANICO e deterministico: nome, comentario EN, PK, fontes).
             Os campos que exigem julgamento (tipo, pii, traducao PT-BR, PK de bronze)
             ficam marcados com `# TODO` para o enriquecimento agentico posterior.
    index    (Re)gera o INDEX.md a partir dos YAMLs da KB — usado para busca eficiente
             sem carregar o conteudo das definicoes no contexto.
    find     Procura tabelas na KB por nome (le apenas o INDEX). Saida: camada | path | comentario.
    copy     Copia deterministicamente um YAML da KB para um destino (passo do /run).

Uso tipico:
    python3 scripts/kb.py import \
        --bronze-src <.../sap/annotations> \
        --gold-src   <.../data_product>
    python3 scripts/kb.py find kna1
    python3 scripts/kb.py copy kna1 --dest schemas/bronze/
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import sys

import yaml

RAIZ_PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(RAIZ_PLUGIN, "knowledge", "sap")
INDEX = os.path.join(KB_DIR, "INDEX.md")

CABECALHO = (
    "# Gerado por scripts/kb.py (mapeamento mecanico). ENRIQUECER antes de usar:\n"
    "#   - traduzir todo `comentario` para PT-BR (fonte esta em EN)\n"
    "#   - definir `tipo` (Spark SQL) de cada coluna\n"
    "#   - classificar `pii` de cada coluna (nenhum|direto|indireto|sensivel)\n"
    "{extra}"
    "# Remova os marcadores `# TODO` conforme enriquecer.\n"
)


def _esc(texto: str) -> str:
    """Escapa uma string para um escalar YAML entre aspas duplas."""
    if texto is None:
        return ""
    return texto.replace("\\", "\\\\").replace('"', '\\"')


def _carrega(caminho: str) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# --------------------------------------------------------------------------- #
# import
# --------------------------------------------------------------------------- #
def _emite_coluna(nome: str, comentario: str, *, nulo: bool) -> str:
    return (
        f"  - nome: {nome}\n"
        f"    tipo: string        # TODO: tipo Spark real (dicionario SAP)\n"
        f'    comentario: "{_esc(comentario)}"   # TODO: traduzir p/ PT-BR\n'
        f"    pii: nenhum         # TODO: classificar PII\n"
        f"    nulo: {'true' if nulo else 'false'}\n"
    )


def _gera_bronze(src_dir: str, out_dir: str) -> list[tuple[str, str, str]]:
    """Cada annotation SAP -> knowledge/sap/bronze/<tabela>.yaml. Retorna (nome,camada,comentario)."""
    os.makedirs(out_dir, exist_ok=True)
    entradas = []
    for caminho in sorted(glob.glob(os.path.join(src_dir, "*.yaml"))):
        tabela = os.path.splitext(os.path.basename(caminho))[0]
        dados = _carrega(caminho)
        desc = (dados.get("description") or "").strip()
        campos = dados.get("fields") or []

        corpo = CABECALHO.format(extra="#   - definir `chave_primaria` (nao consta na fonte bronze)\n")
        corpo += f"tabela: {tabela}\n"
        corpo += "camada: bronze\n"
        corpo += f'comentario: "{_esc(desc)}"   # TODO: traduzir p/ PT-BR\n'
        corpo += "ingestao: cdc\n"
        corpo += f"fonte: sap.{tabela}\n"
        corpo += "chave_primaria: []   # TODO: definir a partir do dicionario SAP\n"
        corpo += "colunas:\n"
        for c in campos:
            corpo += _emite_coluna(c.get("name", ""), (c.get("description") or "").strip(), nulo=True)

        with open(os.path.join(out_dir, f"{tabela}.yaml"), "w", encoding="utf-8") as f:
            f.write(corpo)
        entradas.append((tabela, "bronze", desc))
    return entradas


def _tabelas_do_manifest(caminho_manifest: str) -> list[str]:
    if not os.path.exists(caminho_manifest):
        return []
    dados = _carrega(caminho_manifest)
    tabelas = []
    try:
        grupos = dados["dependencies"]["sapModule"]["tables"]
    except (KeyError, TypeError):
        return []
    for _, lista in (grupos or {}).items():
        for t in (lista or []):
            if t not in tabelas:
                tabelas.append(t)
    return tabelas


def _escolhe_anotacoes(prod_dir: str) -> list[str]:
    """Uma anotacao por 'stem' (tabela do data product); dedup preferindo raiz > s4 > ecc."""
    ann_dir = os.path.join(prod_dir, "annotations")
    todos = sorted(glob.glob(os.path.join(ann_dir, "**", "*.yaml"), recursive=True))
    por_stem: dict[str, str] = {}

    def rank(p: str) -> int:
        rel = os.path.relpath(p, ann_dir)
        if os.sep not in rel:
            return 0
        sub = rel.split(os.sep)[0].lower()
        return {"s4": 1, "ecc": 2}.get(sub, 3)

    for p in todos:
        stem = os.path.splitext(os.path.basename(p))[0]
        if stem not in por_stem or rank(p) < rank(por_stem[stem]):
            por_stem[stem] = p
    return [por_stem[s] for s in sorted(por_stem)]


def _gera_gold(src_dir: str, out_dir: str) -> list[tuple[str, str, str]]:
    """Cada anotacao de data product -> knowledge/sap/gold/<tabela>.yaml (OBT wide)."""
    os.makedirs(out_dir, exist_ok=True)
    entradas = []
    for prod in sorted(os.listdir(src_dir)):
        prod_dir = os.path.join(src_dir, prod)
        if not os.path.isdir(prod_dir):
            continue
        fontes = _tabelas_do_manifest(os.path.join(prod_dir, "manifest.yaml"))
        fontes_yaml = "[" + ", ".join(f"silver.{t}" for t in fontes) + "]" if fontes else "[]"

        for caminho in _escolhe_anotacoes(prod_dir):
            tabela = os.path.splitext(os.path.basename(caminho))[0]
            dados = _carrega(caminho)
            desc = (dados.get("description") or "").strip()
            campos = dados.get("fields") or []

            pks = []
            for c in campos:
                d = (c.get("description") or "").strip()
                if d.endswith(", PK") or d.endswith(",PK"):
                    pks.append(c.get("name", ""))

            corpo = CABECALHO.format(extra="")
            corpo += f"# Data product de origem: {prod}\n"
            corpo += f"tabela: {tabela}\n"
            corpo += "camada: gold\n"
            corpo += f'comentario: "{_esc(desc)}"   # TODO: traduzir p/ PT-BR\n'
            corpo += "entidade: obt              # tabela larga denormalizada (one-big-table)\n"
            corpo += "ingestao: custom\n"
            corpo += f"fontes: {fontes_yaml}   # tabelas SAP de origem (join custom no transform)\n"
            corpo += f"chave_primaria: [{', '.join(pks)}]\n"
            corpo += "colunas:\n"
            for c in campos:
                d = (c.get("description") or "").strip()
                nome = c.get("name", "")
                d_limpo = d[: -len(", PK")].rstrip() if d.endswith(", PK") else (
                    d[: -len(",PK")].rstrip() if d.endswith(",PK") else d
                )
                corpo += _emite_coluna(nome, d_limpo, nulo=(nome not in pks))

            with open(os.path.join(out_dir, f"{tabela}.yaml"), "w", encoding="utf-8") as f:
                f.write(corpo)
            entradas.append((tabela, "gold", desc))
    return entradas


def cmd_import(args) -> int:
    entradas = []
    if args.bronze_src:
        entradas += _gera_bronze(args.bronze_src, os.path.join(KB_DIR, "bronze"))
    if args.gold_src:
        entradas += _gera_gold(args.gold_src, os.path.join(KB_DIR, "gold"))
    _escreve_index()
    n_b = sum(1 for _, c, _ in entradas if c == "bronze")
    n_g = sum(1 for _, c, _ in entradas if c == "gold")
    print(f"KB gerada: {n_b} bronze + {n_g} gold = {len(entradas)} tabelas em {KB_DIR}")
    print(f"INDEX: {INDEX}")
    return 0


# --------------------------------------------------------------------------- #
# index
# --------------------------------------------------------------------------- #
def _entradas_da_kb() -> list[tuple[str, str, str]]:
    entradas = []
    for camada in ("bronze", "gold"):
        for caminho in sorted(glob.glob(os.path.join(KB_DIR, camada, "*.yaml"))):
            dados = _carrega(caminho)
            entradas.append((dados.get("tabela", ""), camada, (dados.get("comentario") or "").strip()))
    return entradas


def _escreve_index(entradas: list | None = None) -> None:
    entradas = entradas if entradas is not None else _entradas_da_kb()
    linhas = [
        "# Indice da base de conhecimento SAP",
        "",
        "Uma linha por tabela: `nome | camada | comentario`. Use para descobrir se uma",
        "tabela/data product ja existe na KB **sem** carregar as definicoes no contexto.",
        "Consulte via `python3 scripts/kb.py find <nome>`.",
        "",
        "| Tabela | Camada | Comentario |",
        "|--------|--------|------------|",
    ]
    for nome, camada, com in sorted(entradas):
        com = com.replace("|", "\\|")
        linhas.append(f"| `{nome}` | {camada} | {com} |")
    os.makedirs(KB_DIR, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def cmd_index(args) -> int:
    entradas = _entradas_da_kb()
    _escreve_index(entradas)
    print(f"INDEX regenerado com {len(entradas)} tabelas: {INDEX}")
    return 0


# --------------------------------------------------------------------------- #
# find
# --------------------------------------------------------------------------- #
def cmd_find(args) -> int:
    alvo = args.nome.lower()
    if not os.path.exists(INDEX):
        print("INDEX inexistente — rode `kb.py import` ou `kb.py index`.", file=sys.stderr)
        return 2
    achou = False
    with open(INDEX, encoding="utf-8") as f:
        for linha in f:
            if not linha.startswith("| `"):
                continue
            partes = [p.strip() for p in linha.strip().strip("|").split("|")]
            if len(partes) < 3:
                continue
            nome = partes[0].strip("`")
            if alvo in nome.lower():
                camada = partes[1]
                caminho = os.path.join("knowledge", "sap", camada, f"{nome}.yaml")
                print(f"{camada}\t{caminho}\t{partes[2]}")
                achou = True
    if not achou:
        print(f"(nenhuma tabela na KB casa com '{args.nome}')")
        return 1
    return 0


# --------------------------------------------------------------------------- #
# copy
# --------------------------------------------------------------------------- #
def cmd_copy(args) -> int:
    origem = None
    for camada in ("bronze", "gold"):
        cand = os.path.join(KB_DIR, camada, f"{args.nome}.yaml")
        if os.path.exists(cand):
            origem = cand
            break
    if origem is None:
        print(f"'{args.nome}' nao esta na KB.", file=sys.stderr)
        return 1
    dest = args.dest
    if os.path.isdir(dest) or dest.endswith(os.sep):
        os.makedirs(dest, exist_ok=True)
        dest = os.path.join(dest, f"{args.nome}.yaml")
    else:
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    shutil.copyfile(origem, dest)
    print(f"copiado: {origem} -> {dest}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Base de conhecimento SAP (bronze/gold) do plugin.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("import", help="gera esqueletos da KB a partir das anotacoes Cortex")
    pi.add_argument("--bronze-src", help="dir .../sap/annotations")
    pi.add_argument("--gold-src", help="dir .../data_product")
    pi.set_defaults(func=cmd_import)

    px = sub.add_parser("index", help="regenera o INDEX.md a partir dos YAMLs da KB")
    px.set_defaults(func=cmd_index)

    pf = sub.add_parser("find", help="procura tabelas na KB por nome (le so o INDEX)")
    pf.add_argument("nome")
    pf.set_defaults(func=cmd_find)

    pc = sub.add_parser("copy", help="copia um YAML da KB para um destino (passo do /run)")
    pc.add_argument("nome")
    pc.add_argument("--dest", required=True, help="arquivo ou diretorio destino")
    pc.set_defaults(func=cmd_copy)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

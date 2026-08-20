#!/usr/bin/env bash
# Inicializa um projeto de engenharia de dados para o ciclo
# validate-state -> specify -> plan -> run:
#   1. cria o scaffold (.data-eng/, schemas/, resources/, src/notebooks/, databricks.yml)
#   2. aplica as permissoes padrao em .claude/settings.json (merge nao-destrutivo)
# Uso: init.sh [--root <raiz-do-projeto>] [--dry-run]
set -euo pipefail

REPO_ROOT="$PWD"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) REPO_ROOT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -*) echo "erro: flag desconhecida $1" >&2; exit 2 ;;
    *) echo "erro: argumento inesperado $1" >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null || { echo "erro: jq nao encontrado (brew install jq)" >&2; exit 1; }

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES="$PLUGIN_ROOT/templates"
SETTINGS="$REPO_ROOT/.claude/settings.json"

# --- permissoes: uniao das listas allow/ask/deny com o que ja existe
CURRENT='{}'
[[ -f "$SETTINGS" ]] && CURRENT="$(cat "$SETTINGS")"
MERGED="$(jq -n --argjson cur "$CURRENT" --slurpfile tpl "$TEMPLATES/settings.json" '
  $tpl[0] as $t
  | reduce ("allow","ask","deny") as $k
      ($cur; .permissions[$k] = (((.permissions[$k] // []) + ($t.permissions[$k] // [])) | unique))
')"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "--- scaffold que seria criado em $REPO_ROOT (arquivos existentes sao preservados)"
  printf '    %s\n' \
    .data-eng/specs/ .data-eng/plans/ .data-eng/outputs/ .data-eng/guidelines/ \
    schemas/bronze/ schemas/silver/ schemas/gold/ \
    resources/etl.job.yml \
    src/notebooks/ingest_cdc.py src/notebooks/scd_type1.py src/notebooks/transform_gold.py \
    databricks.yml
  (cd "$TEMPLATES/guidelines" && printf '    .data-eng/guidelines/%s\n' *.md)
  echo
  echo "--- .claude/settings.json apos merge (nao gravado)"
  echo "$MERGED" | jq '.permissions'
  exit 0
fi

# --- scaffold (idempotente: mkdir -p e copia-se-nao-existe, nunca sobrescreve)
# copia_se_ausente evita `cp -n`, que no BSD/macOS retorna 1 quando o destino existe.
copia_se_ausente() { [[ -e "$2" ]] || cp "$1" "$2"; }

mkdir -p "$REPO_ROOT"/.data-eng/{specs,plans,outputs,guidelines}
mkdir -p "$REPO_ROOT"/schemas/{bronze,silver,gold}
mkdir -p "$REPO_ROOT"/resources "$REPO_ROOT"/src/notebooks

for f in "$TEMPLATES"/guidelines/*.md; do
  copia_se_ausente "$f" "$REPO_ROOT/.data-eng/guidelines/$(basename "$f")"
done
copia_se_ausente "$TEMPLATES/databricks.yml"           "$REPO_ROOT/databricks.yml"
copia_se_ausente "$TEMPLATES/resources/etl.job.yml"    "$REPO_ROOT/resources/etl.job.yml"
copia_se_ausente "$TEMPLATES/notebooks/ingest_cdc.py"     "$REPO_ROOT/src/notebooks/ingest_cdc.py"
copia_se_ausente "$TEMPLATES/notebooks/scd_type1.py"      "$REPO_ROOT/src/notebooks/scd_type1.py"
copia_se_ausente "$TEMPLATES/notebooks/transform_gold.py" "$REPO_ROOT/src/notebooks/transform_gold.py"

echo "scaffold pronto em: $REPO_ROOT"
find "$REPO_ROOT/.data-eng" "$REPO_ROOT/schemas" "$REPO_ROOT/resources" "$REPO_ROOT/src" \
     "$REPO_ROOT/databricks.yml" -mindepth 0 2>/dev/null | sed "s|^$REPO_ROOT/|  |" | sort

# --- permissoes
mkdir -p "$REPO_ROOT/.claude"
if [[ -f "$SETTINGS" ]]; then
  cp "$SETTINGS" "$SETTINGS.bak"
  echo
  echo "backup: .claude/settings.json.bak"
fi
echo "$MERGED" > "$SETTINGS"
echo "permissoes aplicadas: .claude/settings.json"

echo
echo "proximos passos:"
echo "  - preencha os campos <PREENCHER> em databricks.yml (fonte unica de config)"
echo "  - defina as tabelas de origem em schemas/bronze/ (um YAML por tabela)"
echo "  - rode a skill validate-state para conferir o estado local x Unity Catalog"

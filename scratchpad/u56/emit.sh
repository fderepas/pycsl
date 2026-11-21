#!/bin/bash
# emit the mirror .mlw (no proof) of the 8 files with call-site rejections, into scratchpad/u56/emit
ROOT=/home/fabrice/git/pycsl-u56; cd "$ROOT" || exit 2
OUT=${1:-$ROOT/scratchpad/u56/emit}; mkdir -p "$OUT"
for rel in module6_whyml/statements module6_whyml/stmt_control_flow module6_whyml/expressions module6_whyml/functions module6_whyml/types frontend/pure_ast frontend/Module1_Ingestor proof2why3/sertop; do
  f=src/self-annotate/src/$rel.py; m=${f%.py}.mlw
  git ls-files --error-unmatch "$m" >/dev/null 2>&1 && { echo "TRACKED $m"; continue; }
  rm -f "$m"
  PYTHONHASHSEED=0 timeout 900 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck --keep-mlw --import-path src/pycsl "$f" > "$OUT/${rel//\//__}.emit.log" 2>&1
  echo "$rel rc=$?"; [ -f "$m" ] && mv "$m" "$OUT/${rel//\//__}.mlw"
done

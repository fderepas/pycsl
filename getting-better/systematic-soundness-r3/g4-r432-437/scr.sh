#!/bin/bash
# scr.sh <tree> <outdir> <mode-flag: --no-proof|--full> <jobs> FILE... ; run AS heavy.sh (QUICK class when --no-proof)
T=$1; O=$2; M=$3; J=$4; shift 4
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
mkdir -p "$O/out"; : > "$O/verdicts.tsv"
one() {
  T=$1; O=$2; M=$3; f=$4
  k=$(basename "$f" .py); o="$O/out/$k.out"
  flag=""; [ "$M" = --no-proof ] && flag="--no-proof"
  ( cd "$T" && PYTHONHASHSEED=0 timeout 400 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path "$(dirname "$f")" --import-path src/pycsl $flag > "$o" 2>&1 ); rc=$?
  if grep -q "Verification SUCCESS" "$o"; then v=PROVED
  elif [ $rc = 124 ]; then v=TIMEOUT
  elif grep -qE "PYCSL-[A-Z0-9-]+" "$o" && ! grep -q "Prover result is" "$o"; then v=REFUSED
  elif grep -q "Prover result is" "$o"; then v=FAIL
  elif [ -n "$flag" ] && [ $rc = 0 ]; then v=TYPECHECKS
  else v=REFUSED
  fi
  code=$(grep -oE "PYCSL-[A-Z0-9-]+" "$o" | head -1)
  printf '%s\t%s\t%s\t%s\n' "$k" "$rc" "$v" "${code:--}" >> "$O/verdicts.tsv"
}
export -f one
printf '%s\n' "$@" | xargs -P "$J" -I{} bash -c 'one "$@"' _ "$T" "$O" "$M" {}
sort -o "$O/verdicts.tsv" "$O/verdicts.tsv"; echo DONE

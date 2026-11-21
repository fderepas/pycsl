#!/bin/bash
# screen.sh <tree> <outdir> <mode: np|full> <jobs> FILE...  : run pycsl from <tree> on each probe (cwd = <tree>,
# --import-path <probe dir>), one line per file in <outdir>/verdicts.tsv: file rc verdict code.
# Run it as ONE heavy.sh job (internal -P <jobs>).  Skips files already present in verdicts.tsv.
T=$1; O=$2; M=$3; J=$4; shift 4
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
mkdir -p "$O/out"; touch "$O/verdicts.tsv"
one() {
  T=$1; O=$2; M=$3; f=$4
  k=$(echo "$f" | sed 's|/home/fabrice/git/[^/]*/||; s|[^A-Za-z0-9]|_|g')
  o="$O/out/$k.$M.out"
  flag=""; [ "$M" = np ] && flag="--no-proof"
  ( cd "$T" && PYTHONHASHSEED=0 timeout 400 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path "$(dirname "$f")" --import-path src/pycsl $flag > "$o" 2>&1 ); rc=$?
  if grep -q "Verification SUCCESS" "$o"; then v=PROVED
  elif [ $rc = 124 ]; then v=TIMEOUT
  elif grep -qE "PYCSL-[A-Z0-9-]+" "$o" && ! grep -q "Prover result is" "$o"; then v=REFUSED
  elif grep -q "Prover result is" "$o"; then v=FAIL
  elif [ "$M" = np ] && [ $rc = 0 ]; then v=TYPECHECKS
  else v=REFUSED
  fi
  code=$(grep -oE "PYCSL-[A-Z0-9-]+" "$o" | head -1)
  printf '%s\t%s\t%s\t%s\n' "$f" "$rc" "$v" "${code:--}" >> "$O/verdicts.tsv"
}
export -f one
for f in "$@"; do grep -qF "$f	" "$O/verdicts.tsv" || echo "$f"; done | xargs -P "$J" -I{} bash -c 'one "$@"' _ "$T" "$O" "$M" {}

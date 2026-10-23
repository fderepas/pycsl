#!/usr/bin/env bash
# Parallel .mlw emission sweep for byte-diff gates. Uses HALF the CPU cores
# (via the canonical get_cpu_count in lib-cpu.sh) and --no-typecheck (emission only,
# no per-file why3 call). Usage: byte-diff-sweep.sh <out-dir>
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-cpu.sh"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"; PY="$ROOT/.venv/bin/python3"
OUT="$1"; mkdir -p "$OUT"; JOBS=3
emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"; name=$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  rm -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw"
  $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
  [ -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" ] && \
    mv "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" "$OUT/$name.mlw"
}
export -f emit_one
# (#45) THE GLOB USED TO BE `0*.py`. The corpus crossed 1000 in relaunch #44, so
# `1000_module_global_field_store_erasure.py` and `1001_..._faithful.py` — route #28's
# OWN witnesses — were silently outside every byte-diff this plane has ever run, and
# every witness added from here on would have been too. A sweep that stops growing with
# the corpus reports the same green whether the new files are inert or not.
SRC=$(ls "$ROOT"/test-suite/corpus/pycsl-reference/*.py)
NSRC=$(printf '%s\n' "$SRC" | wc -l)
# Zero-input / shrinking-input guard (the #44 rule: a gate that cannot tell "nothing is
# wrong" from "I looked at nothing" is not a gate). 900 is below the measured 931 at #45
# and the corpus only grows; a drop past it means the glob or the corpus path is broken.
if [ "$NSRC" -lt 900 ]; then
  echo "[!] byte-diff-sweep: only $NSRC source file(s) matched — the corpus glob is broken. NOT A PASS." >&2
  exit 2
fi
printf '%s\n' "$SRC" | xargs -P "$JOBS" -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
echo "emitted $(ls "$OUT" 2>/dev/null | wc -l) of $NSRC source file(s) into $OUT ($JOBS jobs)"

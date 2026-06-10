#!/usr/bin/env bash
# Parallel .mlw emission sweep for byte-diff gates. Uses HALF the CPU cores
# (via the canonical get_cpu_count in lib-cpu.sh) and --no-typecheck (emission only,
# no per-file why3 call). Usage: byte-diff-sweep.sh <out-dir>
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-cpu.sh"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"; PY="$ROOT/.venv/bin/python3"
OUT="$1"; mkdir -p "$OUT"; JOBS=$(half_cpu_jobs)
emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"; name=$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  rm -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw"
  $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
  [ -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" ] && \
    mv "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" "$OUT/$name.mlw"
}
export -f emit_one
ls "$ROOT"/test-suite/corpus/pycsl-reference/0*.py | xargs -P "$JOBS" -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
echo "emitted $(ls "$OUT" 2>/dev/null | wc -l) into $OUT ($JOBS jobs)"

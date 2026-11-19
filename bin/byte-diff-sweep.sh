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
# THE SOURCE MANIFEST. Without it, `byte-diff-compare.py` cannot tell a corpus file that
# was ADDED since the baseline (benign) from one whose REFUSAL BECAME AN EMISSION (a
# soundness loss, and how route #42 was reopened under a green byte-diff). One line here
# makes that distinction exact instead of a judgement call.
printf '%s\n' "$SRC" | xargs -n1 basename > "$OUT/SOURCES.txt"
printf '%s\n' "$SRC" | xargs -P "$JOBS" -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
echo "emitted $(ls "$OUT" 2>/dev/null | wc -l) of $NSRC source file(s) into $OUT ($JOBS jobs)"

# ===================================================================================
# (#49) ROUTE #60 — THE SECOND CORPUS. Everything above sweeps ONLY
# `test-suite/corpus/pycsl-reference`. `test-suite/corpus/python-reference` is 2200+
# files and A LIVE PROVED SUITE (`bin/run-reference-tests.sh`), and it was outside every
# byte-diff this gate has ever run. That is the SAME defect as the `0*.py` glob recorded
# above, one level up: a sweep whose population stops short reports the same green
# whether the files it never looked at are inert or not.
#
# MEASURED, not hypothesised: route #60's first (blunt) repair was byte-inert over
# `pycsl-reference` — 923/923, zero differing — and BROKE `python-reference/0050.py`, a
# PROVED driver, which no gate would have caught.
#
# The second corpus goes into a `pyref/` SUBDIRECTORY so that consumers which take this
# directory as an `--emit-dir` of the CORPUS (`bin/check-clause-survival.py`, and the
# shared emission in `bin/run-soundness-planes.sh`) see an unchanged top level — they
# list `*.mlw` non-recursively, so the subdirectory is invisible to them. A landing
# compares BOTH: `byte-diff-compare.py BASE CAND` and
# `byte-diff-compare.py BASE/pyref CAND/pyref --min-files 2000`.
PYREF_ROOT="$ROOT/test-suite/corpus/python-reference"
if [ -d "$PYREF_ROOT" ]; then
  POUT="$OUT/pyref"; mkdir -p "$POUT"
  emit_pyref() {
    f="$1"; POUT="$2"; ROOT="$3"; PY="$4"
    rel="${f#$ROOT/test-suite/corpus/python-reference/}"
    name="pyref__$(printf '%s' "${rel%.py}" | tr '/' '_')"
    d=$(dirname "$f"); b=$(basename "$f" .py)
    flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
    rm -f "$d/$b.mlw"
    $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
    [ -f "$d/$b.mlw" ] && mv "$d/$b.mlw" "$POUT/$name.mlw"
  }
  export -f emit_pyref
  PSRC=$(find "$PYREF_ROOT" -name '*.py')
  NPSRC=$(printf '%s\n' "$PSRC" | wc -l)
  # Same zero-input / shrinking-input guard as the first corpus. 2000 is below the
  # measured 2217 and this corpus only grows.
  if [ "$NPSRC" -lt 2000 ]; then
    echo "[!] byte-diff-sweep: only $NPSRC python-reference source file(s) matched — the glob is broken. NOT A PASS." >&2
    exit 2
  fi
  # The manifest, in the SAME `<name>.py` form `byte-diff-compare.py` expects, so an
  # ADDED driver is told apart from a REFUSAL THAT BECAME AN EMISSION here too.
  printf '%s\n' "$PSRC" | while IFS= read -r f; do
    rel="${f#$PYREF_ROOT/}"; printf 'pyref__%s.py\n' "$(printf '%s' "${rel%.py}" | tr '/' '_')"
  done > "$POUT/SOURCES.txt"
  printf '%s\n' "$PSRC" | xargs -P "$JOBS" -I{} bash -c 'emit_pyref "$@"' _ {} "$POUT" "$ROOT" "$PY"
  echo "emitted $(ls "$POUT"/*.mlw 2>/dev/null | wc -l) of $NPSRC python-reference file(s) into $POUT ($JOBS jobs)"
fi

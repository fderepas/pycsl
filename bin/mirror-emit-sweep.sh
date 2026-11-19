#!/usr/bin/env bash
# mirror-emit-sweep — the MIRROR half of the L3 byte-inertness plane, made executable.
#
# WHY THIS EXISTS. `bin/byte-diff-sweep.sh` emits the 900+ file CORPUS into a directory so
# `bin/byte-diff-compare.py` can diff two of them. The MIRROR half of the same plane — the
# 53 files under `src/self-annotate/src/` — has never had a script: every window rewrote a
# shell loop for it, and window #50 recorded that as the reason a one-sided sweep missed
# route #42's reopening ("my sweeps check GONE and not APPEARED"). `byte-diff-compare.py`
# was made executable at `681acc25` and now fails on MOVED / GONE / **APPEARED**; this
# script gives it the mirror population to compare, in the same SOURCES.txt-manifest shape
# the corpus sweep uses, so an ADDED mirror file is told apart from a refusal-turned-
# emission EXACTLY rather than by judgement.
#
# CAUTION: the emitter writes `--keep-mlw` output NEXT TO THE SOURCE, so this sweep
# transiently creates and deletes `.mlw` files inside the TRACKED `src/self-annotate/`
# tree. It refuses to touch any path git already tracks (see emit_one). Do not run it
# while a whole-file mirror proof battery is writing into the same tree.
#
# Usage: mirror-emit-sweep.sh <out-dir>
# Then:  bin/byte-diff-compare.py <baseline-dir> <candidate-dir> --min-files 45
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-cpu.sh"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY="$ROOT/.venv/bin/python3"; [ -x "$PY" ] || PY=python3
OUT="$1"; mkdir -p "$OUT"; JOBS=$(half_cpu_jobs)

emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"
  # Flatten the mirror's directory structure into one path-keyed .mlw so
  # byte-diff-compare.py can diff two output directories the way it does for the corpus.
  # KEY BY RELATIVE PATH, NOT BASENAME (relaunch #51). The mirror has FOUR `__init__.py`
  # files (src/, frontend/, proof2why3/, module6_whyml/), so a basename key is NOT
  # injective — 53 files collapse to 50 keys. Any ad-hoc mirror byte-diff that flattened
  # by basename was silently comparing the wrong pairs, or overwriting, for those files.
  name=$(printf '%s' "${f#"$ROOT/src/self-annotate/src/"}" | sed 's/\.py$//; s#/#__#g')
  # SAFETY (relaunch #51, a near-miss paid for in my own tree). The emitter writes its
  # `--keep-mlw` output NEXT TO THE SOURCE, so this sweep transiently creates and deletes
  # files inside `src/self-annotate/`, WHICH IS A TRACKED DIRECTORY. A blind `rm -f` there
  # can destroy a committed artefact: `src/self-annotate/pycsl-wp-spec.mlw` is tracked.
  # (That one is safe by accident — it has no sibling .py and lives one level up — and an
  # accident is not a guard.) NEVER remove a TRACKED path here.
  if git -C "$ROOT" ls-files --error-unmatch "${f%.py}.mlw" >/dev/null 2>&1; then
    echo "[!] mirror-emit-sweep: ${f%.py}.mlw is TRACKED — refusing to overwrite a committed artefact." >&2
    return 0
  fi
  rm -f "${f%.py}.mlw"
  PYTHONHASHSEED=0 timeout 900 "$PY" "$ROOT/src/pycsl/pycsl.py" \
      --no-proof --no-typecheck --keep-mlw --import-path "$ROOT/src/pycsl" \
      "$f" >/dev/null 2>&1
  [ -f "${f%.py}.mlw" ] && mv "${f%.py}.mlw" "$OUT/$name.mlw"
}
export -f emit_one

SRC=$(find "$ROOT/src/self-annotate/src" -name '*.py' | sort)
NSRC=$(printf '%s\n' "$SRC" | wc -l)

# Zero-input / shrinking-input guard (the #44 rule: a gate that cannot distinguish
# "nothing is wrong" from "I looked at nothing" is not a gate). 45 is below the measured
# 53 and the mirror only grows.
if [ "$NSRC" -lt 45 ]; then
  echo "[!] mirror-emit-sweep: only $NSRC mirror source file(s) found — the mirror path is broken. NOT A PASS." >&2
  exit 2
fi

# Injectivity guard: the flattened key must be one-to-one, or two mirror files would
# silently overwrite each other's emission and the diff would compare the wrong pair while
# reporting a confident zero. The key is the relative path with `/` -> `__`, which is
# injective by construction; this re-checks it rather than trusting the construction,
# because the FIRST version of this script keyed on basename and 53 files collapsed to 50.
NKEY=$(printf '%s\n' "$SRC" | sed "s#^$ROOT/src/self-annotate/src/##; s/\.py$//; s#/#__#g" | sort -u | wc -l)
if [ "$NKEY" -ne "$NSRC" ]; then
  echo "[!] mirror-emit-sweep: $NSRC file(s) but only $NKEY distinct key(s) — the" >&2
  echo "    flattened key is not injective and emissions would overwrite each other." >&2
  echo "    NOT A PASS." >&2
  exit 2
fi

# THE SOURCE MANIFEST, same contract as the corpus sweep: without it byte-diff-compare.py
# cannot tell a mirror file ADDED since the baseline (benign) from one whose REFUSAL
# BECAME AN EMISSION (a soundness loss, and exactly how route #42 stayed hidden).
printf '%s\n' "$SRC" | sed "s#^$ROOT/src/self-annotate/src/##; s/\.py$//; s#/#__#g; s/$/.mlw/" | sort > "$OUT/SOURCES.txt"

printf '%s\n' "$SRC" | xargs -P "$JOBS" -I {} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"

NEMIT=$(ls -1 "$OUT"/*.mlw 2>/dev/null | wc -l)
echo "[*] mirror-emit-sweep: emitted $NEMIT of $NSRC mirror file(s) into $OUT"
echo "    Compare with: bin/byte-diff-compare.py <baseline> $OUT --min-files 45"

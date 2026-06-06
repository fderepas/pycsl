#!/usr/bin/env bash
# extraction-byte-diff.sh — CC.5 byte-diff validation.
#
# Compares the Rocq-extracted emit_stmt_full_complete (run via the
# OCaml driver) against Module 6's Python _stmts_to_whyml on each
# test case in test-suite/extraction-byte-diff/cases.txt.
#
# Closes the loop on the Sub-α correspondence theorem: with the
# composition lemma proved (Phase6L_EmitComposition.v) and this
# tool reporting zero byte-diffs, the residual narrowed axiom
# `module6_actual_matches_formal` is empirically validated per-
# corpus.
#
# Usage:   bin/extraction-byte-diff.sh
# Exits:   0 if all cases agree, 1 if any case differs, 2 on setup error
#
# Architecture:
#
#   ┌────────────────────┐        ┌───────────────────────┐
#   │  cases.txt         │        │ Phase6L_EmitExtract.v │
#   │  (case names)      │        │      → OCaml          │
#   └──────────┬─────────┘        └───────────┬───────────┘
#              │                              │
#              │                              ▼
#              │                  ┌────────────────────────┐
#              │                  │  driver.ml (extracted) │
#              │                  │  → driver binary       │
#              │                  └───────────┬────────────┘
#              │                              │
#              ├──────────────────────────────┤
#              │                              │
#              ▼                              ▼
#   ┌─────────────────────┐       ┌────────────────────────┐
#   │ extraction-byte-    │       │  driver                │
#   │ diff.py (Python)    │       │  Rocq-extracted output │
#   │ Module 6 output     │       │                        │
#   └──────────┬──────────┘       └───────────┬────────────┘
#              │                              │
#              └────────────► diff ◄──────────┘

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROCQ="${ROOT}/src/formal-semantics/rocq"
EXTRACTED="${ROCQ}/extracted"
PY_TOOL="${ROOT}/bin/extraction-byte-diff.py"

# ----- Phase 1: ensure extraction is built. -----
if [[ ! -f "${EXTRACTED}/EmitExtract.ml" ]]; then
  echo "[setup] Extracting Phase6L_EmitExtract.v ..."
  ( cd "${ROCQ}" && make Phase6L_EmitExtract.vo ) || {
    echo "[error] Rocq extraction failed." >&2
    exit 2
  }
fi

# ----- Phase 2: ensure OCaml driver is compiled. -----
if [[ ! -x "${EXTRACTED}/driver" ]] || \
   [[ "${EXTRACTED}/driver.ml" -nt "${EXTRACTED}/driver" ]] || \
   [[ "${EXTRACTED}/EmitExtract.ml" -nt "${EXTRACTED}/driver" ]]; then
  echo "[setup] Compiling OCaml driver ..."
  ( cd "${EXTRACTED}" \
      && ocamlc -c EmitExtract.mli \
      && ocamlc -c EmitExtract.ml \
      && ocamlc -c driver.ml \
      && ocamlc -o driver EmitExtract.cmo driver.cmo ) || {
    echo "[error] OCaml driver compilation failed." >&2
    exit 2
  }
fi

# ----- Phase 3: run both sides and capture per-case output. -----
ROCQ_OUT="$(mktemp -t byte-diff.rocq.XXXX)"
PY_OUT="$(mktemp -t byte-diff.py.XXXX)"
trap 'rm -f "${ROCQ_OUT}" "${PY_OUT}"' EXIT

"${EXTRACTED}/driver" > "${ROCQ_OUT}" || {
  echo "[error] Rocq-extracted driver failed." >&2
  exit 2
}
python3 "${PY_TOOL}" > "${PY_OUT}" || {
  echo "[error] Python driver failed." >&2
  exit 2
}

# ----- Phase 4: per-case diff. -----
declare -i passed=0 failed=0
printf "%-22s %-32s %-32s %s\n" "CASE" "ROCQ-EXTRACTED" "MODULE 6 PYTHON" "RESULT"
printf "%-22s %-32s %-32s %s\n" "----" "--------------" "---------------" "------"

while IFS=$'\t' read -r case_id rocq_out; do
  py_line="$(grep "^${case_id}"$'\t' "${PY_OUT}" 2>/dev/null || true)"
  py_out="${py_line#*$'\t'}"
  if [[ -z "${py_line}" ]]; then
    printf "%-22s %-32s %-32s %s\n" \
      "${case_id}" "${rocq_out:0:32}" "(missing)" "MISSING"
    failed=$((failed+1))
    continue
  fi
  if [[ "${rocq_out}" == "${py_out}" ]]; then
    printf "%-22s %-32s %-32s %s\n" \
      "${case_id}" "${rocq_out:0:32}" "${py_out:0:32}" "PASS"
    passed=$((passed+1))
  else
    printf "%-22s %-32s %-32s %s\n" \
      "${case_id}" "${rocq_out:0:32}" "${py_out:0:32}" "DIFF"
    failed=$((failed+1))
  fi
done < "${ROCQ_OUT}"

echo
echo "[summary] PASSED: ${passed}    FAILED: ${failed}"
echo
if [[ ${failed} -gt 0 ]]; then
  echo "[note] Initial cases.txt likely shows several DIFFs — Module 6"
  echo "       emits indented + trailing-rest-aware WhyML; the formal"
  echo "       Rocq pretty-printer is indentation-free. Diffs document"
  echo "       the presentational gaps captured in the Sub-α file"
  echo "       headers (notably Sub-α.2 ref-deref / let-syntax-trailing-rest)."
  echo "       The PASSING cases empirically validate the byte-equivalent"
  echo "       fragment of the correspondence."
  exit 1
fi
exit 0

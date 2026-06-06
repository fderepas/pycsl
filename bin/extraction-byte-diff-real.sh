#!/usr/bin/env bash
# extraction-byte-diff-real.sh — CC.5 byte-diff on REAL PyCSL programs.
#
# Pipeline per `.py` source in test-suite/extraction-byte-diff/
# reference-cases/:
#
#   1. Module 5 (via pycsl-ir-dump.py) → IR JSON
#   2. ir-to-rocq-ast.py --driver <tmp>/driver.ml
#         → OCaml driver source with whyml_stmt literal
#   3. ocamlc driver.ml linked with extracted EmitExtract.cmo
#         → driver binary
#   4. Run driver → Rocq-extracted state-aware output
#   5. Run Module 6 on the same IR → Module 6 output
#   6. diff
#
# Sources OUTSIDE the simple subset (the converter rejects them with
# `NotInSimpleSubset`) are reported as SKIP.

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROCQ="${ROOT}/src/formal-semantics/rocq"
EXTRACTED="${ROCQ}/extracted"
CASES_DIR="${ROOT}/test-suite/extraction-byte-diff/reference-cases"
REAL_CORPUS="${ROOT}/test-suite/corpus/pycsl-reference"
PY_VENV="${ROOT}/.venv/bin/python"

# Cases come from the curated synthetic set plus a survey of real-corpus
# tests. Real-corpus tests are SKIPPED unless they fit the simple subset.
# Real-corpus tests (out of 386) whose body fits the converter's
# subset. Discovered by surveying all tests with bin/ir-to-rocq-ast.py.
# History:
#   - Initial (Pass/Assign/AugAssign/ArraySet only): 19 tests
#   - After While/If + comparisons + If-Return reject: 30 tests
SURVEY_REAL_TESTS=(
  0004 0005 0007 0013 0014 0017 0031 0032 0034 0044
  0045 0046 0070 0072 0073 0074 0075 0078 0079 0088
  0089 0090 0091 0096 0097 0120 0121 0122 0123 0126
  0146 0148 0149 0150 0151 0203 0206 0210 0211 0212
  0213 0214 0215 0216 0217 0218 0219 0220 0221 0222
  0223 0250 0251 0252 0253 0257 0258 0259 0260 0261
  0263 0264 0265 0266 0267 0268 0269 0270 0271 0274
  0276 0277 0278 0279 0280 0287 0293 0297 0300 0301
  0326 0335 0337 0368 0383
)

# ----- Phase 1: Rocq extraction + EmitExtract.cmo -----
if [[ ! -f "${EXTRACTED}/EmitExtract.ml" ]]; then
  ( cd "${ROCQ}" && make Phase6L_EmitExtract.vo ) >/dev/null || {
    echo "[error] Rocq extraction failed." >&2
    exit 2
  }
fi
if [[ ! -f "${EXTRACTED}/EmitExtract.cmo" ]]; then
  ( cd "${EXTRACTED}" \
      && ocamlc -c EmitExtract.mli \
      && ocamlc -c EmitExtract.ml ) || {
    echo "[error] OCaml compilation of EmitExtract failed." >&2
    exit 2
  }
fi

# ----- Phase 2: per-case driver compilation and run -----
WORK="$(mktemp -d -t byte-diff-real.XXXX)"
trap 'rm -rf "${WORK}"' EXIT

declare -i passed=0 failed=0 skipped=0
printf "%-22s %-36s %-36s %s\n" "CASE" "ROCQ-EXTRACTED" "MODULE 6" "RESULT"
printf "%-22s %-36s %-36s %s\n" "----" "--------------" "--------" "------"

run_module6() {
  local src="$1"
  local case_id="$2"
  "${PY_VENV}" - "${src}" "${case_id}" "${ROOT}" <<'PYEOF'
import json, sys
src, case_id, root = sys.argv[1], sys.argv[2], sys.argv[3]
from pathlib import Path
ROOT = Path(root)
for cand in (ROOT / ".venv" / "lib").glob("python*/site-packages"):
    sys.path.insert(0, str(cand))
sys.path.insert(0, str(ROOT / "src" / "pycsl"))
sys.path.insert(0, str(ROOT / "bin"))
from importlib import import_module
ird = import_module("pycsl-ir-dump")
ir = json.loads(ird.dump_ir(src))
fn = ir["functions"][0]
body = [s for s in fn.get("body", []) if s.get("stmt") != "Return"]

from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler
ir_shell = {
    "functions": [], "shared_vars": [], "globals": [],
    "module_methods": [], "imports": [], "type_decls": [],
    "abstract_ops": [], "memory_model": "hoare",
}
t = Module6_WhyMLTranspiler(json.dumps(ir_shell))
t._reset_function_state({"bounded_int": None}, [])
declared = set()
local_refs = set()
for s in body:
    if s.get("stmt") == "Assign":
        declared.add(s["target"])
        local_refs.add(s["target"])
out = t._stmts_to_whyml(body, local_refs, declared, "", in_loop=False)
out = "\n".join(ln.lstrip() for ln in out.split("\n"))
print(f"{case_id}\t{json.dumps(out)}")
PYEOF
}

SOURCES=("${CASES_DIR}"/*.py)
for n in "${SURVEY_REAL_TESTS[@]}"; do
  if [[ -f "${REAL_CORPUS}/${n}.py" ]]; then
    SOURCES+=("${REAL_CORPUS}/${n}.py")
  fi
done

for src in "${SOURCES[@]}"; do
  case_id="$(basename "${src}" .py)"
  # OCaml requires module names to start with a letter and have no dashes.
  ml_name="$(echo "${case_id}" | tr '-' '_')"
  driver_ml="${WORK}/${ml_name}.ml"
  "${PY_VENV}" "${ROOT}/bin/ir-to-rocq-ast.py" "${src}" \
      --driver "${driver_ml}" > /dev/null 2> "${WORK}/conv.err"
  rc=$?
  if [[ ${rc} -ne 0 ]]; then
    reason="$(head -1 "${WORK}/conv.err")"
    printf "%-22s %-36s %-36s %s\n" \
      "${case_id}" "(not in subset)" "—" "SKIP"
    echo "        ${reason}" >&2
    skipped=$((skipped + 1))
    continue
  fi
  bin="${WORK}/${ml_name}"
  ( cd "${WORK}" && \
      ocamlc -I "${EXTRACTED}" -c "${ml_name}.ml" 2>"${WORK}/ocaml.err" && \
      ocamlc -I "${EXTRACTED}" -o "${bin}" \
          "${EXTRACTED}/EmitExtract.cmo" "${ml_name}.cmo" 2>>"${WORK}/ocaml.err"
  ) || {
    printf "%-22s %-36s %-36s %s\n" \
      "${case_id}" "(OCaml fail)" "—" "OCAML-FAIL"
    head -5 "${WORK}/ocaml.err" >&2
    failed=$((failed + 1))
    continue
  }
  rocq_line="$("${bin}")"
  rocq_out="${rocq_line#*$'\t'}"
  py_line="$(run_module6 "${src}" "${case_id}")"
  py_out="${py_line#*$'\t'}"
  if [[ "${rocq_out}" == "${py_out}" ]]; then
    printf "%-22s %-36s %-36s %s\n" \
      "${case_id}" "${rocq_out:0:36}" "${py_out:0:36}" "PASS"
    passed=$((passed + 1))
  else
    printf "%-22s %-36s %-36s %s\n" \
      "${case_id}" "${rocq_out:0:36}" "${py_out:0:36}" "DIFF"
    failed=$((failed + 1))
  fi
done

echo
echo "[summary] PASSED: ${passed}    DIFF: ${failed}    SKIPPED: ${skipped}"
[[ ${failed} -eq 0 ]]

#!/usr/bin/env bash
# Run BOTH IR conformance corpora — the published front-end <-> core contract test
# (docs/ir.md §10; refactor.md Phase E). This is the ENFORCEMENT half of the IR freeze:
#
#   * core corpus     (bin/core-only-conformance.py)     — the CORE honors the IR with no
#                                                           front-end: golden IR -> byte-
#                                                           identical WhyML. A core change
#                                                           that breaks golden-IR->WhyML
#                                                           fails here.
#   * front-end corpus (bin/frontend-only-conformance.py) — the Python FRONT-END produces
#                                                           the canonical IR with no prover:
#                                                           source -> resolved IR matching
#                                                           the frozen golden. A front-end
#                                                           change that breaks source->IR
#                                                           fails here.
#
# Exit 0 iff BOTH corpora pass (currently 38/38 each). Used standalone and as an additive
# gate step in bin/run-reference-tests.sh.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Prefer the project venv's python (same selection as run-reference-tests.sh).
if [ -x "$PROJECT_ROOT/.venv/bin/python3" ]; then
    PY="$PROJECT_ROOT/.venv/bin/python3"
else
    PY="python3"
fi

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

rc=0

echo "[*] IR conformance — core corpus (golden IR -> WhyML, no front-end)"
if "$PY" "$SCRIPT_DIR/core-only-conformance.py"; then
    echo -e "  ${GREEN}[OK]${RESET} core-only conformance"
else
    echo -e "  ${RED}[FAIL]${RESET} core-only conformance"
    rc=1
fi

echo "[*] IR conformance — front-end corpus (source -> resolved IR, no prover)"
if "$PY" "$SCRIPT_DIR/frontend-only-conformance.py"; then
    echo -e "  ${GREEN}[OK]${RESET} front-end-only conformance"
else
    echo -e "  ${RED}[FAIL]${RESET} front-end-only conformance"
    rc=1
fi

if [ "$rc" -eq 0 ]; then
    echo -e "${GREEN}[+] IR conformance: both corpora pass — front-end<->core contract intact.${RESET}"
else
    echo -e "${RED}[!] IR conformance FAILED — the IR contract (docs/ir.md §10) regressed.${RESET}"
fi
exit "$rc"

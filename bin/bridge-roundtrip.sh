#!/usr/bin/env bash
# bridge-roundtrip.sh — P0.3 of richer-contracts-bridge-plan.md.
#
# The CI round-trip for the formal<->mirror richer-contracts bridge.  On a
# formal-side change it re-establishes the whole chain and fails loudly if any
# link drifts:
#
#   1. RE-STATEMENT CROSS-CHECK  (P0.1) — the WhyML export EmitAssignExport
#      .emit_F_assign still agrees with the certified Rocq emit_assign.
#   2. REGENERATE CONTRACTS      (P0.2) — the generator reproduces the enriched
#      mirror #@ contracts from the export (idempotent).
#   3. LINT                      (P0.2) — no hand-written enriched bridge ensures.
#   4. RE-PROVE MIRROR           — the affected mirror file(s) still verify.
#   5. FIDELITY                  — the self-annotation mirror is body-faithful.
#   6. LEDGER == 3               — git diff of src/formal-semantics + the axiom
#      allowlist is empty (the re-statement cross-check is an AUDIT test, not a
#      soundness axiom; the 3-axiom ledger is untouched).
#   7. CORPUS BYTE-DIFF 0        — the generator only writes #@ lines into mirror
#      .py files, never emitter code, so corpus emission is byte-identical by
#      construction; asserted via a clean `git status src/pycsl`.
#
# Usage:  bin/bridge-roundtrip.sh
# Exit:   0 all green; 1 a gate failed; 2 setup error.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
FAIL=0
step() { printf '\n\033[1m========== %s ==========\033[0m\n' "$1"; }

step "1/7  RE-STATEMENT CROSS-CHECK (WhyML emit_F_assign == Rocq emit_assign)"
if bin/bridge-restatement-check.sh --timeout 12; then
  echo "[+] cross-check PASS"
else
  echo "[!] cross-check FAILED — the WhyML re-statement drifted from Rocq emit_assign"; FAIL=1
fi

step "2/7  REGENERATE BRIDGE CONTRACTS (generate-don't-write; idempotent)"
if python3 bin/gen-bridge-contracts.py --check; then
  echo "[+] generator idempotent"
else
  echo "[!] generator NOT idempotent — mirror contracts are stale; run gen-bridge-contracts.py"; FAIL=1
fi

step "3/7  LINT (no hand-written enriched bridge ensures)"
if python3 bin/gen-bridge-contracts.py --lint; then
  echo "[+] lint clean"
else
  echo "[!] lint FAILED — a bridge #@ ensures was hand-written (drift vector §4)"; FAIL=1
fi

step "4/7  RE-PROVE AFFECTED MIRROR FILE(S)"
MIRRORS=$(python3 - <<'PY'
import importlib.util, os
spec = importlib.util.spec_from_file_location("g", "bin/gen-bridge-contracts.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(" ".join(sorted({e["file"] for e in m.REGISTRY})))
PY
)
for rel in $MIRRORS; do
  f="src/self-annotate/src/$rel"
  echo "--- proving $f ---"
  if python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl 2>/dev/null | grep -q "Verification SUCCESS"; then
    echo "[+] $rel: Verification SUCCESS"
  else
    echo "[!] $rel: verification FAILED"; FAIL=1
  fi
done

step "5/7  FIDELITY (mirror body-faithful to live emitter)"
if bin/self-annotate-mirror-check.sh >/dev/null 2>&1; then
  echo "[+] mirror-check green"
else
  echo "[!] mirror-check FAILED"; FAIL=1
fi

step "6/7  LEDGER == 3 (no new axiom; formal-semantics + allowlist untouched)"
LED=$(git diff HEAD -- src/formal-semantics '**/proof_axiom_allowlist.py' | wc -l | tr -d ' ')
if [ "$LED" = "0" ]; then
  echo "[+] ledger held: git diff on src/formal-semantics + allowlist is EMPTY"
else
  echo "[!] LEDGER TOUCHED: $LED diff lines under src/formal-semantics / allowlist"; FAIL=1
fi

step "7/7  CORPUS BYTE-DIFF 0 (mirror-gated: emitter untouched)"
DIRTY=$(git status --porcelain src/pycsl | wc -l | tr -d ' ')
if [ "$DIRTY" = "0" ]; then
  echo "[+] src/pycsl clean: generator wrote only mirror #@ lines => corpus emission byte-identical"
else
  echo "[!] src/pycsl DIRTY ($DIRTY files): the generator touched emitter code — run byte-diff-sweep.sh"; FAIL=1
fi

echo
if [ "$FAIL" = "0" ]; then
  echo "==================== BRIDGE ROUND-TRIP: GREEN ===================="
  exit 0
else
  echo "==================== BRIDGE ROUND-TRIP: RED ======================"
  exit 1
fi

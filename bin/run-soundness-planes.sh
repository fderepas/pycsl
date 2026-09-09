#!/usr/bin/env bash
# run-soundness-planes — RUN EVERY DRIVER-RUN LOWER BOUND, IN ONE COMMAND.
#
# WHY THIS EXISTS. `bin/run-reference-tests.sh` gates on exactly two things: doc-coherency
# and IR conformance. Every other lower bound this campaign built — the mirror-fidelity
# plane, the trusted-directive count, the ratchets over erasure/vacuity/type-keyed constant
# answers, and the rest — fires ONLY when a driver session remembers to run it. That has
# cost the campaign four times now:
#
#   * window #49 found `check-trusted-raises-honesty` RED AT HEAD with nobody looking;
#   * window #50 found the 27th plane's baseline STALE, and only because it happened to
#     change the arm that plane classifies;
#   * window #50 found ROUTE #42 REOPENED AND LIVE AT HEAD FOR A WHOLE WINDOW, because the
#     suite that would have said so had not been run to completion since route #52 landed;
#   * window #51 found `check-getattr-erasure` red (a stale ratchet) AND
#     `check-self-annotate-mirror-sync` — AN L-PLANE — red at HEAD, long-standing.
#
# A lower bound nobody runs is not a lower bound, it is a note. This script turns the notes
# back into bounds. It is DELIBERATELY CHEAP (pure AST/grep planes only, no proving, no
# corpus emission) so that it can eventually be wired into the reference-test runner as a
# leading gate the way doc-coherency already is.
#
# THE #44 RULE IS ENFORCED HERE TOO: a gate that cannot tell "nothing is wrong" from "I
# looked at nothing" is not a gate. If fewer than MIN_PLANES planes actually ran, this
# script exits 2 — a REFUSAL, not a pass.
#
# EXIT CODES
#   0  every plane green
#   1  at least one plane red (its name and rc are printed)
#   2  refusal: fewer than MIN_PLANES planes were found/ran, so the result means nothing
#
# Skip with PYCSL_SKIP_SOUNDNESS_PLANES=1.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "${PYCSL_SKIP_SOUNDNESS_PLANES:-0}" = "1" ]; then
    echo "[*] soundness-planes: skipped via PYCSL_SKIP_SOUNDNESS_PLANES=1"
    exit 0
fi

# The FAST set: every plane that is pure static analysis (no proving, no corpus emission).
# Measured at 37403f79 on a loaded 12-core box; the whole set is ~2 minutes, of which
# check-trusted-raises-honesty is ~50s. Planes that self-emit the mirror or drive the
# prover (getattr-erasure, computed-rhs-erasure, yield-erasure, shadowed-selfcalls,
# untrusted-emitted, trusted-frame-honesty, swallowed-exceptions, bespoke-model-drift,
# internal-crash-free, param-mutator-visibility) are DELIBERATELY EXCLUDED: they cost
# minutes each and belong in a driver battery, not in a per-run gate. avatar-frame-parity
# and clause-survival are excluded because they REQUIRE an --emit-dir.
PLANES=(
    check-self-annotate-mirror-sync.py
    count-trusted-directives.py
    check-mirror-coverage.py
    check-mirror-field-parity.py
    check-mirror-loop-annotations.py
    check-mirror-signature-drift.py
    check-refusal-reachability.py
    check-trusted-raises-honesty.py
    check-type-keyed-constant-answers.py
    check-emit-ir-arm-postconditions.py
    check-singleton-constant-lowering.py
    check-type-keyed-value-sentinels.py
    check-collapsed-option-reads.py
    check-constant-fallthrough.py
    check-dropped-mutation.py
    check-ir-field-coverage.py
    check-statement-block-coverage.py
    check-vacuous-drivers.py
)
MIN_PLANES=18

ran=0
failed=()
echo "[*] soundness-planes: running ${#PLANES[@]} driver-run lower bound(s)"
for p in "${PLANES[@]}"; do
    if [ ! -f "$PROJECT_ROOT/bin/$p" ]; then
        echo "    MISSING  $p"
        continue
    fi
    out="$(cd "$PROJECT_ROOT" && python3 "bin/$p" 2>&1)"
    rc=$?
    ran=$((ran + 1))
    if [ "$rc" -eq 0 ]; then
        printf '    ok       %-42s\n' "$p"
    else
        printf '    RED      %-42s rc=%s\n' "$p" "$rc"
        echo "$out" | tail -3 | sed 's/^/               /'
        failed+=("$p(rc=$rc)")
    fi
done

if [ "$ran" -lt "$MIN_PLANES" ]; then
    echo "[!] soundness-planes: REFUSING — only $ran plane(s) ran, expected at least $MIN_PLANES."
    echo "    This is not a pass. A gate that cannot tell 'nothing is wrong' from"
    echo "    'I looked at nothing' is not a gate (the #44 rule)."
    exit 2
fi

if [ "${#failed[@]}" -ne 0 ]; then
    echo "[!] soundness-planes: ${#failed[@]} of $ran RED — ${failed[*]}"
    exit 1
fi

echo "[+] soundness-planes: OK — all $ran plane(s) green."
exit 0

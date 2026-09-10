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

# THE SLOW SET, opt-in with `--slow` (or PYCSL_SOUNDNESS_PLANES_SLOW=1).
#
# These ten self-emit the mirror or drive the prover, so they do not belong in a per-run
# gate — but "not in the per-run gate" had quietly become "nobody runs them at all", and
# A SIGNAL NOBODY COLLECTS IS NOT A SIGNAL. The cost was also overstated by the note
# above: measured on this box they are ~2 minutes EACH and several share the same mirror
# emission, so the whole set is ~20 minutes, not the "session-scale" the exclusion implied.
# What that gap cost, concretely: window #51 found `check-getattr-erasure` RED on a stale
# ratchet, and generation #3 found `check-shadowed-selfcalls` RED at 15 — both had been
# red at HEAD with nobody looking, which is exactly the failure this script was written
# to end for the fast set.
#
# ONE EMISSION, SHARED. Six of these accept `--emit-dir` and each was otherwise emitting
# all 53 mirrors for itself. `--slow` now emits ONCE into a temp dir and hands it to those
# six, which both shortens the set and makes every one of them see the SAME emission —
# planes that disagree because they each emitted separately is a failure this repo has
# already had (see the note in check-avatar-frame-parity.py about three `--emit-dir`
# arguments pointing at different directories and "agreeing").
#
# `check-avatar-frame-parity` joins the set for the first time as a result: it REQUIRES an
# `--emit-dir` and so could not be run bare by this loop at all.
#
# `count-trusted-directives` runs a SECOND time here with the dir, because its stale-marker
# half — "is a `\trusted`-marked function nonetheless emitted as a definition?" — is gated
# on `emit_dir` and therefore never ran in the per-run battery. Measured at the tree this
# was added on: stale 0.
#
# `check-mirror-type-only` is here because it belongs here by this file's own taxonomy — it
# EMITS, so it is not a "pure static analysis" plane — but it is the cheapest gate in the
# repo when it reuses the shared emission (~10s) and it has TWICE been the difference
# between a green battery and a four-hour whole-file proof reporting the same thing:
# route #57's ill-typed landing, and the staged-L1 landing. **A MIRROR EDIT MUST BE
# TYPE-CHECKED BEFORE IT IS PROVED**, and the fast set cannot do it without emitting.
#
# `check-clause-survival` is still NOT here, and the reason is specific rather than
# incidental: its `--emit-dir` wants a freshly emitted CORPUS (bin/byte-diff-sweep.sh), not
# the mirror. Handing it this directory would silently compare the wrong population.
SLOW_PLANES=(
    check-getattr-erasure.py
    check-computed-rhs-erasure.py
    check-yield-erasure.py
    check-shadowed-selfcalls.py
    check-untrusted-emitted.py
    check-trusted-frame-honesty.py
    check-swallowed-exceptions.py
    check-bespoke-model-drift.py
    check-internal-crash-free.py
    check-param-mutator-visibility.py
    check-avatar-frame-parity.py
    count-trusted-directives.py
    check-mirror-type-only.py
)
# Planes that take the shared mirror emission. Anything not listed runs bare, exactly as
# before.
EMIT_DIR_PLANES=" check-computed-rhs-erasure.py check-yield-erasure.py check-shadowed-selfcalls.py check-trusted-frame-honesty.py check-avatar-frame-parity.py count-trusted-directives.py check-mirror-type-only.py "
SHARED_EMIT=""

if [ "${1:-}" = "--slow" ] || [ "${PYCSL_SOUNDNESS_PLANES_SLOW:-0}" = "1" ]; then
    PLANES+=("${SLOW_PLANES[@]}")
    # The refusal guard scales with the set, or `--slow` would silently weaken it.
    MIN_PLANES=$((MIN_PLANES + ${#SLOW_PLANES[@]}))
    echo "[*] soundness-planes: --slow, adding ${#SLOW_PLANES[@]} prover/emission plane(s) (~20 min)"
    SHARED_EMIT="$(mktemp -d "${TMPDIR:-/tmp}/pycsl-planes-emit.XXXXXX")"
    trap 'rm -rf "$SHARED_EMIT"' EXIT
    # THE FILE NAMING IS LOAD-BEARING AND IT IS NOT OBVIOUS. Every consumer maps a `.mlw`
    # back to its source with `os.path.relpath(src, MIRROR)[:-3].replace(os.sep, "_")` —
    # ONE underscore. `scratchpad/w49/emit-mirrors.sh` writes TWO (`${rel//\//__}`), and
    # feeding that directory to these planes is not a loud failure: measured, it makes
    # check-yield-erasure report 0 generators where a bare run reports 3 (A FALSE GREEN)
    # and check-trusted-frame-honesty report "RATCHET BROKEN — 48 > 0" (A FALSE RED).
    # That is precisely the hazard check-avatar-frame-parity.py's own header warns about,
    # three --emit-dir arguments pointing at directories and "agreeing". So the emission is
    # inlined here with the right convention rather than delegated to a helper whose
    # convention can drift out from under it.
    _py="$PROJECT_ROOT/.venv/bin/python3"; [ -x "$_py" ] || _py=python3
    while IFS= read -r _src; do
        _rel="${_src#"$PROJECT_ROOT/src/self-annotate/src/"}"
        _name="${_rel%.py}"; _name="${_name//\//_}"
        rm -f "${_src%.py}.mlw"
        (cd "$PROJECT_ROOT" && PYTHONHASHSEED=0 "$_py" src/pycsl/pycsl.py "$_src" \
            --import-path "$PROJECT_ROOT/src/pycsl" --no-proof --keep-mlw) >/dev/null 2>&1
        [ -f "${_src%.py}.mlw" ] && mv "${_src%.py}.mlw" "$SHARED_EMIT/$_name.mlw"
    done < <(find "$PROJECT_ROOT/src/self-annotate/src" -name '*.py' | sort)
    NEMIT=$(ls "$SHARED_EMIT"/*.mlw 2>/dev/null | wc -l)
    # A SHARED EMISSION THAT SILENTLY CAME UP SHORT WOULD WEAKEN SIX PLANES AT ONCE, so it
    # gets the same #44 treatment as everything else: refuse rather than run them on it.
    if [ "$NEMIT" -lt 40 ]; then
        echo "[!] soundness-planes: REFUSING — the shared mirror emission produced only"
        echo "    $NEMIT .mlw file(s), expected at least 40. Six --slow planes would have"
        echo "    been fed a truncated population. THIS IS A REFUSAL, NOT A PASS."
        exit 2
    fi
    echo "[*] soundness-planes: shared mirror emission ready ($NEMIT .mlw) — six plane(s) will use it"
fi

ran=0
failed=()
echo "[*] soundness-planes: running ${#PLANES[@]} driver-run lower bound(s)"
for p in "${PLANES[@]}"; do
    if [ ! -f "$PROJECT_ROOT/bin/$p" ]; then
        echo "    MISSING  $p"
        continue
    fi
    if [ -n "$SHARED_EMIT" ] && [[ "$EMIT_DIR_PLANES" == *" $p "* ]]; then
        out="$(cd "$PROJECT_ROOT" && python3 "bin/$p" --emit-dir "$SHARED_EMIT" 2>&1)"
    else
        out="$(cd "$PROJECT_ROOT" && python3 "bin/$p" 2>&1)"
    fi
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

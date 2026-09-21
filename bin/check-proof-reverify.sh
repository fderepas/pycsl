#!/usr/bin/env bash
# check-proof-reverify.sh — THE AXIOM-FOOTPRINT GATE for `#@ proof` citations.
#
# WHY THIS EXISTS, and it is the fourth gate of its kind this campaign has had to
# collect. A `#@ proof rocq|lean <qualname>` directive IMPORTS the cited theorem into
# the Why3 ledger AS AN AXIOM. The whole trust argument for that import is that the
# cited theorem is itself PROVED — closed under the global context, or closed under a
# short allow-list of kernel axioms (`propext`, `Quot.sound`, …). Nothing in the
# 40-plane battery checked that.
#
# MEASURED, gen #30. Replacing a CITED theorem's `Qed` with `Admitted` in
# `test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v`:
#   * `bin/check-proof-crosscheck.sh` stays at 17 PASS / 16 SKIP / 0 FAIL, rc=0 — it
#     compares STATEMENTS, which are unchanged, and is right not to notice;
#   * the reference suite stays green — pycsl.py's proof replay COMPILES the file, and
#     an `Admitted` compiles;
#   * `pycsl.py <file> --audit-proof --reverify-proofs` DOES catch it
#     ("has non-allowlisted assumptions", rc=1) — and NO script in `bin/`, no
#     test-suite runner and no Makefile target ever passes that flag.
#
# So the check existed, worked, and was never run. This script runs it.
#
# NOTE the flag pairing, which cost time to discover: `--reverify-proofs` is a MODIFIER
# on `--audit-proof`. Passing it alone is silently ignored and the run looks like an
# ordinary green verification.
#
# CAUTION, TWO ARTIFACT SIDE EFFECTS, both the same class as the cross-check gate's:
#   * `.audit-cache/` is a TRACKED, hash-keyed cache of footprint results. A run adds
#     UNTRACKED entries for anything it measures fresh. They are cache, not evidence —
#     `git clean -f .audit-cache/` after a worktree run. The hash key is what makes the
#     cache safe: editing a cited proof changes it, and the control below confirms the
#     gate still goes red through a warm cache (`reverify-cached … non-allowlisted`).
#   * this RECOMPILES the cited Rocq/Lean proofs and
#     therefore dirties tracked `.vo` / `.olean` / `.aux` artifacts under `*.proofs/`.
# Run it in a worktree, not in a checkout you are editing.
set -u
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="${PROJECT_ROOT}/.venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"
[ -x "$PYTHON" ] || { echo "[!] no python3 found." >&2; exit 2; }

eval "$(opam env --switch=coq-4.14 2>/dev/null)" || true

total_pass=0
total_skip=0
total_soundfail=0
total_unresolved=0
n_files=0
soundfail_files=()

# THE UNRESOLVED RATCHET, and why it is a ratchet rather than a pass.
# On first collection (gen #30) this gate reported SIX failures on a CLEAN tree, and
# every one of them is an INSTRUMENT condition rather than an unsound citation:
#   * 0420.py x3 — `UnixFs.Struct.i1a1/i18/i2.round_trip`: "proof dir not found
#     .../0420.proofs/rocq". The cited proofs live in the `unix-filesystem/` tree; the
#     audit looks in `<file>.proofs/<prover>/` by default and is not told otherwise.
#   * 0712.py x2 — `UnixFs.Field.field_to_str_round_trip` (rocq AND lean): "namespace
#     path 'UnixFs.Field' not present" — the same cross-tree citation shape.
#   * 0778.py x1 — `Pycsl.Struct.Std.round_trip_i32i32` (lean): the footprint line was
#     not parsed ("#print axioms line missing"). The Lean source was READ and the
#     theorem is a genuine proof with no `sorry`, so this is an output-parse miss in
#     `audit_proof_reverify.py`, not an axiom.
# "I could not measure it" must never be reported as "it is unsound", and it must never
# be reported as a pass either. So they are counted apart, held at a ratchet, and the
# NEXT step is named: teach the audit the cross-tree proof paths (5 of 6) and fix the
# Lean footprint parse (1 of 6), then lower this to 0.
UNRESOLVED_RATCHET=6

candidates=(
    "src/self-annotate/src/"*.py
    "src/self-annotate/src/module6_whyml/"*.py
    "test-suite/corpus/pycsl-reference/"*.py
    "unix-filesystem/UnixInodeFileSystem.py"
)

for f in "${candidates[@]}"; do
    [ -f "$f" ] || continue
    grep -q "^#@ proof " "$f" || continue
    # A `# pycsl-expected: FAIL` corpus file is a NEGATIVE test — its citations are not
    # claims this project makes. Same exclusion, and same reason, as the cross-check gate.
    grep -q "^# pycsl-expected: FAIL" "$f" && continue

    n_files=$((n_files + 1))
    out="$("$PYTHON" src/pycsl/pycsl.py "$f" --audit-proof --reverify-proofs 2>&1)"
    rc=$?
    summary="$(echo "$out" | grep -E '^ +(Passed|Skipped|Failed): ' || true)"
    if [ -z "$summary" ]; then
        echo "[!] proof-reverify: $f produced NO audit summary (rc=$rc). That is not a" >&2
        echo "    measurement — refusing rather than counting it as a pass." >&2
        echo "$out" | tail -5 >&2
        exit 2
    fi
    p=$(echo "$summary" | sed -n 's/.*Passed: *\([0-9][0-9]*\).*/\1/p')
    s=$(echo "$summary" | sed -n 's/.*Skipped: *\([0-9][0-9]*\).*/\1/p')
    d=$(echo "$summary" | sed -n 's/.*Failed: *\([0-9][0-9]*\).*/\1/p')
    total_pass=$((total_pass + ${p:-0}))
    total_skip=$((total_skip + ${s:-0}))
    # (total_fail retired: failures are split into SOUNDNESS vs UNRESOLVED below)
    # SPLIT the failures: a parsed, non-allowlisted assumption set is a SOUNDNESS
    # failure; "proof dir not found" / "namespace path not present" / "#print axioms
    # line missing" are INSTRUMENT conditions and are counted apart.
    if [ "${d:-0}" -gt 0 ] || [ "$rc" -ne 0 ]; then
        fails="$(echo "$out" | grep -E '^ +✗' || true)"
        unres="$(echo "$fails" | grep -cE 'proof dir not found|namespace path .* not present|line missing' || true)"
        sound=$(( ${d:-0} - ${unres:-0} ))
        total_unresolved=$((total_unresolved + ${unres:-0}))
        if [ "$sound" -gt 0 ]; then
            total_soundfail=$((total_soundfail + sound))
            soundfail_files+=("$f")
            echo "  [SOUNDNESS-FAIL] $f"
            echo "$fails" | grep -vE 'proof dir not found|namespace path .* not present|line missing' | sed 's/^/     /'
        else
            echo "  [unresolved] $f ($unres citation(s) the audit could not locate or parse)"
        fi
    fi
done

echo "=== Axiom-footprint reverify over $n_files annotated file(s) ==="
echo "  VERIFIED:   $total_pass"
echo "  SKIPPED:    $total_skip"
echo "  UNRESOLVED: $total_unresolved  (ratchet $UNRESOLVED_RATCHET)"
echo "  SOUNDNESS:  $total_soundfail"

# THE ZERO-CHECK REFUSAL (route #44's rule, and the lesson of the cross-check facade):
# "I looked at nothing" is not a gate.
if [ "$n_files" -eq 0 ] || [ "$total_pass" -eq 0 ]; then
    echo "[!] proof-reverify: $n_files file(s), $total_pass citation(s) verified — that is" >&2
    echo "    not a measurement. The candidate globs or the directive grep are broken." >&2
    exit 2
fi

if [ "$total_soundfail" -gt 0 ]; then
    echo "[-] proof-reverify: ${#soundfail_files[@]} file(s) cite a theorem whose assumption" >&2
    echo "    set is NOT in the kernel-axiom allow-list. A cited theorem that is Admitted," >&2
    echo "    or that rests on an axiom of its own, imports THAT into the Why3 ledger —" >&2
    echo "    which is exactly what the ledger==3 claim says does not happen." >&2
    exit 1
fi

if [ "$total_unresolved" -gt "$UNRESOLVED_RATCHET" ]; then
    echo "[-] proof-reverify: $total_unresolved unresolved citation(s) > ratchet" >&2
    echo "    $UNRESOLVED_RATCHET. A citation the audit cannot locate or parse is an" >&2
    echo "    UNCHECKED axiom import. Resolve it or move the ratchet DELIBERATELY." >&2
    exit 1
fi

echo "[+] proof-reverify: OK — $total_pass cited theorem(s) closed under the allow-list," \
     "$total_unresolved unresolved at the ratchet."
exit 0

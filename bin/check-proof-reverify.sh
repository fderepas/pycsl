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
#     *** AS OF gen #31 THE RUN CLEANS UP AFTER ITSELF — see the epilogue below. ***
# Run it in a worktree, not in a checkout you are editing.
#
# ---------------------------------------------------------------------------------------
# ARTIFACT SELF-CLEANING (gen #31), and the NEAR-MISS that motivated it.
# ---------------------------------------------------------------------------------------
# A `--slow` battery left 13 TRACKED `.aux` files modified under
# `test-suite/corpus/pycsl-reference/*.proofs/rocq/` plus ~26 UNTRACKED `.tmp*.aux`,
# because this gate recompiles the cited proofs IN PLACE. Two generations then had to
# decide, every single run, whether a dirty `.aux` was work or exhaust — and gen #30 came
# within one command of answering it destructively: an `rm -f .../rocq/.tmp*.aux` typed to
# clear the exhaust DELETED SEVERAL HUNDRED TRACKED FILES. 990 build artifacts are tracked
# in this repository (611 `.aux`, 94 each of `.vo`/`.vok`/`.vos`/`.glob`, 3 `.olean`), so
# a glob aimed at that directory is aimed at all of them.
#
# The repair is NOT a glob and NOT an untracking sweep (removing the shipped `.vo` files
# would change what the proof replay reads). It is a BEFORE/AFTER snapshot of `git status`
# restricted to the proof trees: whatever THIS RUN dirtied is restored, and whatever was
# already dirty when the run started is left exactly as it was found. Untracked files the
# run created are removed BY EXPLICIT NAME, one `rm -f --` per path, never by pattern; a
# path containing whitespace is skipped rather than guessed at. `git checkout --` is used
# only on a file this run modified or deleted and that was clean beforehand, so the
# standing rule "never discard tracked changes you did not make" is enforced by the
# snapshot rather than by memory.
#
# Set `PROOF_REVERIFY_KEEP_ARTIFACTS=1` to keep the exhaust (debugging a recompile).
# ---------------------------------------------------------------------------------------
set -u
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

_ART_SCOPE=(
    "test-suite/corpus/pycsl-reference"
    "test-suite/corpus/python-reference"
    "unix-filesystem"
    ".audit-cache"
)
_ART_BEFORE="$(mktemp)"; _ART_AFTER="$(mktemp)"
# THE SNAPSHOT IS KEYED ON THE PATH, NOT ON THE STATUS LINE, and that distinction is the
# whole safety property. A first draft matched whole `git status` lines; a file that was
# already ` M` before the run and that the run then DELETED came back as ` D`, the line no
# longer matched, and the epilogue "restored" it — silently discarding a pre-existing
# change, which is precisely the accident this epilogue exists to prevent. Caught by the
# isolated fixture in `getting-better/` rather than by a real run, because a real run only
# shows it the day somebody is mid-edit.
git status --porcelain -- "${_ART_SCOPE[@]}" 2>/dev/null \
    | sed -e "s/^...//" -e "s/^.* -> //" > "$_ART_BEFORE" || : > "$_ART_BEFORE"

_art_restore() {
    local rc=$?
    [ "${PROOF_REVERIFY_KEEP_ARTIFACTS:-0}" = "1" ] && { rm -f "$_ART_BEFORE" "$_ART_AFTER"; return $rc; }
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        git status --porcelain -- "${_ART_SCOPE[@]}" > "$_ART_AFTER" 2>/dev/null || : > "$_ART_AFTER"
        local n_rm=0 n_co=0 n_skip=0 st path line
        while IFS= read -r line; do
            st="${line:0:2}"; path="${line:3}"
            [ -n "$path" ] || continue
            case "$path" in *[[:space:]]*) continue ;; esac      # never guess at a quoted path
            grep -qxF -- "$path" "$_ART_BEFORE" && continue      # this PATH was already dirty
            case "$path" in
                # An UNTRACKED DIRECTORY (`?? .audit-cache/`) collapses an unknown number of
                # files into one line, so removing it would be a pattern delete wearing a
                # path. Report it and leave it; the header already names `git clean -f` for
                # the one directory this gate can create from nothing.
                */) n_skip=$((n_skip + 1)); continue ;;
            esac
            case "$st" in
                "??") rm -f -- "$path" && n_rm=$((n_rm + 1)) ;;
                *[MTD]*) git checkout -- "$path" 2>/dev/null && n_co=$((n_co + 1)) ;;
            esac
        done < "$_ART_AFTER"
        if [ "$n_rm" -gt 0 ] || [ "$n_co" -gt 0 ] || [ "$n_skip" -gt 0 ]; then
            echo "[*] proof-reverify: cleaned its own build exhaust — removed $n_rm untracked," \
                 "restored $n_co tracked, left $n_skip new untracked director(y/ies) for" \
                 "\`git clean\`. Pre-existing changes untouched."
        fi
    fi
    rm -f "$_ART_BEFORE" "$_ART_AFTER"
    return $rc
}
trap _art_restore EXIT

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
# every one of them was an INSTRUMENT condition rather than an unsound citation. FIVE of
# the six were then FIXED in the same window by giving the audit a cross-tree search path
# (`audit_proof._fallback_proof_dirs`), which took VERIFIED from 155 to 165 — ten
# citations that had never been checked by anything. The ratchet is now ONE. The original
# six, for the record:
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
# be reported as a pass either. So they are counted apart and held at a ratchet.
# THE RATCHET IS NOW ZERO. The last entry was the 0778 Lean footprint parse, and it was
# a PREFIX COLLISION in `audit_proof_reverify.verify_lean_file`: the qualname->line match
# was a SUBSTRING test taking the FIRST hit, and `…round_trip_i32` is a prefix of
# `…round_trip_i32i32`, so the shorter name claimed the longer one's `#print axioms`
# line and the longer one was reported as having a non-allowlisted assumption. Note
# WHICH DIRECTION OF THAT BUG IS THE DANGEROUS ONE: this instance reported a genuine
# proof as an axiom import (loud, harmless), but the same collision could just as easily
# hand a citation SOMEONE ELSE'S clean axiom set and MASK a real one. Fixed by preferring
# the quoted form Lean actually prints and taking the LONGEST match.
# ANY non-zero reading here is now a regression, not a backlog.
UNRESOLVED_RATCHET=0

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

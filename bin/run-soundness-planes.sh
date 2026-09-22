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
    check-trigger-rows-live.py
    check-trusted-raises-honesty.py
    check-type-keyed-constant-answers.py
    check-emit-ir-arm-postconditions.py
    check-singleton-constant-lowering.py
    # (#49) gen #30: the ARGUMENT-COERCION ratchet. Routes #192 and #193 were both
    # substitutions in `_coerce_dotted_args`, found by each other's repair, in one
    # day — the campaign's own "the routes cluster where there is no plane" signature.
    check-argument-coercion.py
    # (#49) gen #30: the FIFTH uncollected gate. `check-trusted-reasons.py` is a full
    # plane — it cross-checks every live `#@ \trusted` marker against a row in
    # `getting-better/trusted-reasons.tsv` in BOTH directions and carries an
    # unclassified ratchet — and NOTHING RAN IT: not this runner, not the suite, not
    # the Makefile. A marker added without a row, a row orphaned by a conversion, or a
    # duplicate, all went unnoticed. It is fast (seconds), so it goes in the fast set.
    check-trusted-reasons.py
    check-type-keyed-value-sentinels.py
    check-collapsed-option-reads.py
    check-constant-fallthrough.py
    check-dropped-mutation.py
    check-ir-field-coverage.py
    check-statement-block-coverage.py
    check-vacuous-drivers.py
    # (#49) gen #30: the RETURN-BOUNDARY ratchet — the gap `check-argument-coercion.py`
    # names in its own header ("the RETURN side ... has no plane yet — the honest gap in
    # this instrument"). Route #198 came out of exactly that gap: a bare `return` lowered
    # to the literal `0`, so an int-returning function PROVED `\result == 0` about `None`.
    # The baseline pins each substituted constant WITH ITS OCCURRENCE COUNT, because a
    # literal-only key would not have caught #198 (`val = "0"` was already blessed for
    # the `False` arm). Demonstrated to FIRE on the pre-#198 emitter via `--live`.
    check-return-boundary-substitutions.py
    # (#49) gen #30: the F-STRING LOWERING ratchet, built on the campaign's own trigger
    # rule (lesson (d): build the plane when TWO routes land in ONE function in ONE day).
    # #199 (the empty f-string was the integer 0) and #203 (a single-part f-string WAS the
    # integer it interpolates) are both `_handle_fstring_expr`, both found this session.
    # It pins the RETURN SET with counts AND two structural tokens, because #203 added a
    # WRAP rather than an exit and the return set alone is green on the pre-#203 tree —
    # measured via `--live`, which is also how that blind spot was found before shipping.
    check-fstring-lowering.py
    # (#49) gen #30: the COERCION-EXIT ratchet — the trigger rule's THIRD firing this
    # session. `check-argument-coercion.py` classifies the `coerced.append(...)` SITES of
    # `_coerce_dotted_args`; it does not look inside the two helpers those sites delegate
    # to, and BOTH produced two routes each (#193/#201 in `_array_coerce_arg`, #194 and
    # #200/#202 in `_coerce_to_int`). Pins both exit sets WITH COUNTS, because
    # `return whyml_str` appears five times across the two functions as five different
    # pass-throughs. Demonstrated to FIRE on the true pre-#201 source via `--live`.
    check-coercion-exits.py
    # (#49) gen #30: the CORPUS-CONTRACT-TRUTH plane. `check-value-differential.py` is the
    # battery's strongest instrument because it CURATES NOTHING — it re-runs CPython on
    # every pass — but its population is 75 files someone chose. 216 PASS-expected corpus
    # files already carry a zero-arg function with a LITERAL `ensures \result == N`, which
    # is directly runnable, so the same measurement extends to the corpus for free. A
    # failure here is the sharpest verdict in the battery: a test that PASSES the prover
    # while its own postcondition is false of its own program. First measurement: 195
    # AGREE, 0 DISAGREE, 21 not runnable standalone (reported, never dropped).
    check-corpus-contract-truth.py
    # (#49) gen #30: the STDLIB-CONTRACT-FIDELITY ratchet. `src/pycsl_lib/` holds 93
    # body-verified stub packages, each CITING the CPython library reference in its
    # docstring, and nothing compared a stub's contract against the function it cites. A
    # contract there is proven OF ITS OWN BODY, so it can be perfectly proven and still be
    # FALSE of the function named in its own citation — this campaign's defect shape, one
    # layer up. Ratchet = the SET of diverging (package, function) pairs, baselined at the
    # two found when the gate was written (`mth.remainder`, `stat.filemode`). NOT a
    # proof-soundness gate TODAY (no name map takes `math` to `mth`, so nothing
    # substitutes these contracts) — it stops the layer drifting further from the stdlib
    # it documents. Self-test: `--selftest-empty-baseline` must exit 1.
    check-stdlib-contract-fidelity.py
    # (#49) gen #30: the PINNED-FACADE ratchet — the STATIC companion to the gate above,
    # and a second gate rather than part of it for a concrete reason: that one CALLS the
    # real stdlib function, so `os` is on its safety deny-list, which puts the sharpest
    # facade set in the layer outside its reach. This one is pure AST. The shape: a body
    # that is a single `return <literal>` AND a contract that PINS that literal — a
    # verified function computing nothing and claiming exactly that. Twelve today, ten of
    # them in `os`; `islink -> 0` is the sharpest (a proof that nothing is ever a
    # symlink). Sound while nothing substitutes this layer for the real module; the set
    # that turns false the day something does.
    check-stdlib-pinned-facades.py
    # (#49) gen #30: the STDLIB TRUST-SURFACE ratchet, and the reason it is a THIRD stdlib
    # gate is the finding itself: the campaign's headline `\trusted` metric does not reach
    # this layer. `count-trusted-directives.py` globs `MIRROR/**/*.py` and
    # `check-trusted-reasons.py` scopes to `src/self-annotate/src`, so the 459 count
    # EXCLUDES `src/pycsl_lib/` — which carries two markers, one of them BARE (no
    # reviewer, no reason: `hlib.Sha256.update`, in a class whose `hexdigest` returns
    # `[0] * 64`). The skill for that layer says it carries ZERO trusted markers. The
    # rule existed, the violation existed, and no plane connected them.
    check-stdlib-trusted-markers.py
)
# (#49) gen #30: TIGHTENED to the EXACT fast-plane count. It had been carrying slack —
# 20 when 22 planes were listed — so a plane could have been deleted from the array and
# the zero-check refusal would still have passed. A floor one below the truth is a gate
# that tolerates exactly the failure it exists to catch. Raise this with the array.
MIN_PLANES=28

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
# `check-clause-survival` IS here as of (#49), with its own emission: its `--emit-dir`
# wants a freshly emitted CORPUS (bin/byte-diff-sweep.sh), not the mirror, and handing it
# THIS directory would silently compare the wrong population — so the loop below emits the
# corpus once, separately, for that plane alone. It was left out for that reason and was
# therefore never run: gen #29 found its ratchet BROKEN (4 deficit files against 2) since
# route #116's witnesses landed.
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
    check-no-exception-differential.py
    check-value-differential.py
    # (#49) gen #29's two new planes. Both run BARE, and that is deliberate: the shared
    # `--emit-dir` above is the MIRROR emission, and `check-assumed-facts` reads the
    # CORPUS (its `assume`/`axiom` families live there), so handing it this directory
    # would compare the wrong population — the same reason `check-clause-survival` is
    # still out. `check-callee-contract-attribution` generates its own drivers.
    check-callee-contract-attribution.py
    check-assumed-facts.py
    check-proof-crosscheck.sh
    # (#49) gen #30: THE AXIOM-FOOTPRINT GATE. `check-proof-crosscheck.sh` above
    # compares a citation's STATEMENT to the cited theorem's; nothing checked that the
    # cited theorem is PROVED. Measured: replacing a cited `Qed` with `Admitted` left
    # the cross-check green, the suite green, and every other plane green — the
    # `--audit-proof --reverify-proofs` footprint check existed, worked, and was run by
    # NOTHING. It recompiles the cited Rocq/Lean proofs, so it belongs in the slow set.
    check-proof-reverify.sh
    check-emitted-vacuity.py
    check-clause-survival.py
)
# Planes that take the shared mirror emission. Anything not listed runs bare, exactly as
# before.
EMIT_DIR_PLANES=" check-computed-rhs-erasure.py check-yield-erasure.py check-shadowed-selfcalls.py check-trusted-frame-honesty.py check-avatar-frame-parity.py count-trusted-directives.py check-mirror-type-only.py "
SHARED_EMIT=""
# (#49) A SECOND shared emission: the CORPUS, for `check-clause-survival.py`.
CORPUS_EMIT=""

if [ "${1:-}" = "--slow" ] || [ "${PYCSL_SOUNDNESS_PLANES_SLOW:-0}" = "1" ]; then
    PLANES+=("${SLOW_PLANES[@]}")
    # The refusal guard scales with the set, or `--slow` would silently weaken it.
    MIN_PLANES=$((MIN_PLANES + ${#SLOW_PLANES[@]}))
    echo "[*] soundness-planes: --slow, adding ${#SLOW_PLANES[@]} prover/emission plane(s) (~20 min)"
    SHARED_EMIT="$(mktemp -d "${TMPDIR:-/tmp}/pycsl-planes-emit.XXXXXX")"
    trap 'rm -rf "$SHARED_EMIT" "$CORPUS_EMIT"' EXIT
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
    elif [ "$p" = "check-clause-survival.py" ]; then
        # (#49) THIS PLANE WANTS A FRESHLY EMITTED CORPUS, not the shared MIRROR emission —
        # handing it the mirror directory would silently compare the wrong population,
        # which is the reason the note above gives for leaving it out. So emit the corpus
        # ONCE, here, and hand it over. It was uncollected, and gen #29 found its ratchet
        # BROKEN (4 deficit files against a ratchet of 2) since route #116's witnesses
        # landed.
        if [ -z "$CORPUS_EMIT" ]; then
            CORPUS_EMIT="$(mktemp -d "${TMPDIR:-/tmp}/pycsl-planes-corpus.XXXXXX")"
            (cd "$PROJECT_ROOT" && bin/byte-diff-sweep.sh "$CORPUS_EMIT" >/dev/null 2>&1) || true
        fi
        out="$(cd "$PROJECT_ROOT" && python3 "bin/$p" --emit-dir "$CORPUS_EMIT" 2>&1)"
    elif [ "$p" = "check-emitted-vacuity.py" ]; then
        # (#49) THIS PLANE NEEDS ITS OWN EMISSION, BESIDE THE MIRROR SOURCES — it reads the
        # `.mlw` next to each `.py` rather than an `--emit-dir`, and WITHOUT `--emit` it
        # REFUSES (rc=2, "found 0 emitted mirror .mlw file(s) ... REFUSING to report a
        # verdict"), which is why it was never in this list. It was therefore UNCOLLECTED,
        # and gen #29 found it RED at HEAD with one erasure outside its ledger. The
        # artefacts are `*.mlw`, which .gitignore already covers.
        out="$(cd "$PROJECT_ROOT" && python3 "bin/$p" --emit 2>&1)"
    elif [[ "$p" == *.sh ]]; then
        # (#49) A PLANE MAY BE A SHELL SCRIPT. `check-proof-crosscheck.sh` is the
        # mechanical 3-way check that a `#@ proof` citation's Why3 axiom says what the
        # cited Rocq/Lean theorem says — the audit that backs every `pycsl_axiom_*` fact
        # the assumed-facts plane classifies as audited-by-construction. It lived only in
        # a Makefile target, and gen #29 found it reporting `PASS 0, SKIP 0, FAIL 0` and
        # rc=0 while checking NOTHING (its `python -m` invocation could not import the
        # package and the error was swallowed). A signal nobody collects is not a signal.
        out="$(cd "$PROJECT_ROOT" && bash "bin/$p" 2>&1)"
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

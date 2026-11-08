# HANDOFF — #43 (2026-09-03, WINDOW 3, relaunch after the #34-#42 `529 Overloaded` outage):
# **the metric did not move (451) and that is again the right answer. This relaunch found
# and closed the TWELFTH demonstrated unsoundness, corrected THREE inherited claims that
# were false, and repaired FIVE gates that were printing their ratchet as if it were their
# measurement.**

## READ THIS FIRST — THREE INHERITED CLAIMS WERE FALSE, AND ALL THREE WERE CHEAP TO CHECK

1. **"A completed 13-file proof battery is waiting to be banked; verdict in
   `scratchpad/w7/verify_arr2.log`" — FALSE.** `verify_arr2.log` is the CORPUS plane. Its
   runner, `scratchpad/w7/verify_arr.sh`, iterates `changed_arr.txt`, which is 26 CORPUS
   TEST FILES, and proves each with `pycsl.py`. `ARR PROVE OK: 26` says nothing about any
   mirror. The mirror battery's verdicts live in `scratchpad/w7/proofs/a_*.rc`: TEN were
   0, `a_expr.rc` was **124** (killed by `pr.sh`'s 10800 s `timeout`, ZERO
   `Verification SUCCESS` lines in its 80514-line log), and `a_m5` / `a_pure` **did not
   exist** — Module5_IREmitter and pure_ast were never started. b952bef5's own commit
   message says so: "STILL OWED: the 13-mirror re-proof battery". The primary record was
   right and the summary of it was wrong. The tell was arithmetic: the count in the log
   line (26) does not match the battery's size (13).
2. **"#34 died mid-implementation of the `nonlocal_writes` IR field" — FALSE.** It is
   landed and witnessed: `Module5_IREmitter.py:5256-5279` builds it, `functions.py:5521`
   refuses on it, corpus **0977** is the witness. Settled by grepping the symbol
   (lesson (az)), in one command.
3. **"Route 6b of the `#@`-attachment audit is open; eight of eleven routes closed" —
   FALSE.** All eleven are closed; 6b is the row in #34's own table marked
   **CLOSED**, banked at 8396828e.

**The one item the #34 handoff named as genuinely unswept — its item 3,
`Module1_Ingestor._assign`'s `elif nxt is None: pass` — was real, and it is route #12
below.** The ladder handed down was stale in three places out of four and correct in the
fourth. Check each item against the disk before spending a minute on it.

## ROUTE #12 — a `#@` DIRECTIVE INSIDE A STATEMENT'S CONTINUATION LINES IS DISCARDED

Reproduced before anything was changed, five probes, every one printing SUCCESS:

    #@ ensures \result == 2
    def f() -> int:
        return (
    #@ assert 1 == 2                  <-- FALSE, AND NEVER CHECKED
            2)
    [+] Verification SUCCESS! All contracts formally proven.

The indented form, the module-level `y: int = (` form of both, and a `#@ ghost x = 99` +
`#@ assert x == 99` PAIR in that position all proved too.

MECHANISM. `_Harvester._assign` associates a comment with a target by `bisect` over the
targets' START lines, so a comment between a leaf statement's first and last line bisects
PAST it. When that statement is the file's last there is no `nxt` at all and the comment
takes `elif nxt is None: pass` or, indented, `prev.footer`. #33's and #34's END-OF-FILE
guards cannot see it: the block does not run to end-of-file — the statement's own
continuation lines follow it.

CLOSED by a refusal spelled INLINE in `Module1_Ingestor.process`, the one place holding
both the tree and the real comment tokens, and `\trusted` in the mirror.
Witness **0979_continuation_directive_refused**, NEGATIVE-TESTED (proves at 13c4860b,
refused at HEAD). Corpus 820/820 byte-identical; mirror L3-tc 53/53; metric unchanged.

**THE CENSUS IS THE PART TO REMEMBER.** A LINE-BASED scan of the 3663 annotated files
reports **95** hits. Every one is `#@` text inside a DOCSTRING — including the
doc-comments of routes 1-11's own witness tests. Tokenizing and keeping only real COMMENT
tokens gives **0**. A refusal built on the line-based number would have rejected 95
innocent files. When you census a SYNTAX, tokenize; a `grep` for `#@` finds the
documentation of the bug as readily as the bug.

## THE `#@`-ATTACHMENT VEIN IS NOW SWEPT

The compound-statement HEADER shapes were the last un-probed family and they are clean:
a directive inside a multi-line `def` signature, a multi-line `while` header and a
multi-line `class` header are all REFUSED by #34's `_reject_misplaced_directives`; one
inside a multi-line `if` condition attaches to the following statement, is CHECKED, and
correctly FAILS. Twelve routes found across #33/#34/#43, twelve closed.

## FIVE GATES WERE REPORTING THEIR RATCHET AS THEIR MEASUREMENT

`check-avatar-frame-parity.py`, `check-computed-rhs-erasure.py`, `check-dropped-mutation.py`,
`check-shadowed-selfcalls.py` and `check-trusted-frame-honesty.py` ended a green run with a
line formatting `args.max_*` — the CONSTANT — and nothing else. #34's closing baseline
copied one of those lines and so recorded "avatar-frame-parity 0 same-file / 7 inherited".
Measured (twice at HEAD, once at 13c4860b, all agreeing): **0 same-file / 1 inherited**.
`MAX_INHERITED` lowered **7 -> 1** — a real tightening, six units of unjustified slack
removed. All five OK lines now print measurement AND ratchet. Every other ratchet is
already AT its measurement, so nothing else could be lowered.

**Corollary for whoever reads a handoff number: a gate's green line is not necessarily a
census. Re-run the gate.**

## THE ARRAY/MAP FRAME EXTENSION — WHERE IT ACTUALLY STANDS

Landed as code at b952bef5 (the deletion of the scalar type filter in
`module6_whyml/functions.py`). Gating status as re-derived by this relaunch:

  · CORPUS byte-diff — **DONE, independently.** 820 emissions at HEAD vs 820 at 13c4860b,
    `diff -rq`: the changed set is EXACTLY the 26 recorded files and nothing else.
  · CORPUS proof — **DONE, freshly.** `43 ARR PROVE OK: 26 / 26`, FAIL empty
    (`scratchpad/w8/verify26.log`).
  · MIRROR battery — **10 / 13.** Green: struct_format, ConcurrencyChecker, audit_proof,
    audit_proof_reverify, proof2why3/parser, types, Module6_WhyMLTranspiler, Module2_Parser,
    stmt_control_flow, module6_whyml/statements. **OWED: `module6_whyml/expressions.py`,
    `frontend/Module5_IREmitter.py`, `frontend/pure_ast.py`.** expressions and
    Module5_IREmitter are IN FLIGHT under `scratchpad/w7/pr2.sh` (28800 s cap, detached
    via `setsid`); pure_ast has not been started.
  · Every NON-PROOF plane — **DONE, all green** (see the gate table below).

**DO NOT BANK THE EXTENSION UNTIL a_expr, a_m5 AND a_pure ARE ALL rc=0.**

## ALSO OWED, AND SMALL: THREE MIRROR RE-PROOFS FOR ROUTE #12

The route-#12 refusal adds exactly ONE line to three mirror emissions —
`raises { PyCSLParseError }` on `val module1_ingestor__process` in
`frontend/Module3_Weaver.mlw`, `frontend/__init__.mlw` and `frontend/ir_resolve.mlw`.
That val is DECLARED BUT NEVER CALLED in all three (grepped), so no goal can move; the
re-proofs are queued behind the array battery rather than skipped on that argument.

## INSTRUMENT FACTS #43 ADDS

18. **THE MIRROR IS `src/self-annotate/src/`, and `src/pycsl/` is the LIVE EMITTER.** Both
    trees carry a file at the same relative path. Proving the wrong one runs to completion
    and refuses *persuasively* — `src/pycsl/module6_whyml/expressions.py` dies with
    `in-place mutation of dict/set parameter 'free'`, a REAL recorded PyCSL boundary. Two
    things settle it, neither of them the error text: a control at an older commit shows
    the same refusal, and the HEAD of a previously-successful log names the file it parsed.
    Canonical invocation (`scratchpad/w2/sweep.sh`): FILE under `src/self-annotate/src/`,
    `--import-path src/pycsl`.
19. **A LIVE-TREE EDIT LEAKS INTO MIRROR EMISSION THROUGH `--import-path src/pycsl`.** The
    mirrors import the LIVE modules, so the live body is what the importer reads. Route
    #12's refusal was first spelled with `%` string formatting; the emitter reads `%` as
    MODULO and pulled the entire `pycsl_div` / `pycsl_mod` preamble into two mirror `.mlw`
    — ten lines of arithmetic helpers, out of a `raise` message. Rewritten with `str()`
    concatenation the delta vanished. "I only touched the live tree" is not an argument for
    emission inertness. Measure it.
20. `bin/check-emitted-vacuity.py` WITHOUT `--emit` does not merely under-report: it prints
    `8 known erasure(s) NO LONGER erased — remove from KNOWN_ERASURES`, i.e. it actively
    invites you to DELETE eight live gates. With `--emit` (11 s) the same eight are
    correctly still erased. Reproduced this window.

## SETTLED, DO NOT RE-DERIVE

* `computed-rhs-erasure`'s two residues are FAITHFULNESS gaps, **not** unsoundnesses.
  `expressions.py::_handle_field_get_expr`'s `_pg2` erases to `0` because
  `_property_getters` lives on `Module6_WhyMLTranspiler` and is read through the mixin, so
  it is not in `_all_record_fields`. The mirror method's contract is
  `requires True / ensures True`, so no false postcondition is provable, and the erased
  branch only RETURNS — it writes nothing, so the frame is over-claimed, which is safe.
  Reopening capability: a cross-class (mixin-owned) field model.
* `dropped-mutation`'s single DROPPED site is `pure_ast._merge_str_constants`'s
  `out[-1].value += v.value` — an augmented store through a non-Name base. The mirror
  method is `\trusted`, so it is a lowering gap, not a converted victim.
* The `UnknownPyExpr -> 0` catch-all is NOT the erasure hazard it looks like for CALLS:
  `xs.count(2)` emits `(xs_count_1 2)`, an opaque function, and three probes with false
  `ensures \result == 0` over an unrecognized local call, a `math.floor` call and a list
  method all correctly FAIL. The `-> 0` path is reached by genexps and yields, which have
  their own planes.

## THE GATE TABLE THIS RELAUNCH RE-RAN FRESH (all green, PATH exported)

    metric                    451 markers / 476 grep / offset 25 / unattached 0
    emitted-vacuity --emit    0 NEW erasure, 8 known gated
    yield-erasure             0 value-erasing, 2 suspension (ratchet 2)
    mirror-signature-drift    0 / 0
    computed-rhs-erasure      measured 2 rhs / 0 param
    dropped-mutation          measured 1 / 50 / 9 / 0
    mirror-field-parity       7 known, 0 NEW
    frame-honesty             trusted 0/0, converted 0 model-visible / 95 total
    untrusted-emitted         865 / 849 / 0 / 0
    shadowed-selfcalls        measured 14
    avatar-frame-parity       measured 0 same-file / 1 inherited (ratchet now 1)
    IR conformance            core-only 38/0, front-end 38/0, 10/10 hashseed-stable
    corpus byte-diff          820 / 820 byte-identical across the route-#12 refusal
    mirror L3-tc              53 / 53, TC_FAIL 0
    fidelity                  both scripts byte-identical to a freshly-built baseline
    doc-coherency             OK

## WHERE THE LADDER STANDS

0. **Finish the array/map battery** (a_expr, a_m5 in flight; a_pure not started), then bank
   the extension. Then the three route-#12 mirror re-proofs.
1. `proof2why3`'s `term` family — the named COST/SCALE residue, needing a general ADT-value
   lowering. Per §A.3 that is NOT a floor; a funded window pays it. It is now the largest
   remaining item.
2. The heterogeneous-list-literal 15.
3. The three formerly authorize-first builds (`find_assigned_vars` structural-variant
   robustification; const-dict global-type-inference model; `while` -> `for` rewrite) —
   pre-authorized since 2026-08-26 and untouched by #33/#34/#43.
4. Housekeeping done this relaunch: the stale worktrees `scratchpad/w3/wt`, `w4/base`,
   `w4/wt` are removed. w3/wt held two uncommitted `src/` edits — the ir_resolve
   qualified-method-name fix (verified LANDED) and an UNLANDED, unproven
   `_Unparser.__init__` conversion, archived to
   `getting-better/interrupted/2026-08-w3-unparser-init-spike.patch`.
   `scratchpad/w7/base` is KEPT: it is the byte-diff baseline.


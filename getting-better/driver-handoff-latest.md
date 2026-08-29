# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-29, RELAUNCH #12 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 513 · grep-substring 538 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep
  hits are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25. Stable across
  three samples.
  **Window #2 delta so far: markers 530 -> 513, grep 555 -> 538.**
  **This session (#12): 516 -> 513 — THREE conversions in two gated increments, plus TWO
  certified boundaries and one CORRECTED refutation.**
- **`bin/check-shadowed-selfcalls.py`: 27 CONVERTED methods / 176 bypassing call sites,
  ratchet 27** — unchanged this session. Needs `TMPDIR` on the repo filesystem
  (`TMPDIR=/home/fabrice/git/pycsl/scratchpad`).
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**, unchanged.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **797 / 780 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**. Corpus byte-diff **0 over 813/813**.
  `frontend/pure_ast` proves **2348 / 2348**; `module6_whyml/functions` **1185 / 1185**.
  `bin/self-annotate-mirror-check.sh` byte-identical to the HEAD baseline.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Commits unpushed by design.

## WHAT THIS SESSION LANDED

1. **`lambda_parameters` + `parse_parameters` CONVERTED (516 -> 514)** — the
   [LIST-ALIAS ELEMENT TYPE] boundary from relaunch #11, broken by the capability its own
   refutation named. TWO markers for ONE capability. Six pieces; the sixth is an
   ELEMENT-TYPE FIXPOINT over the body's assignment graph — seed
   `x.append(<emit_ir local>)`, edge `x = <other seq local>`. **The refutation's "five
   pieces already work" list was HALF RIGHT**: `_emit_ir_seq_locals` was EMPTY at the
   construction site, so the append SEED was missing too. Re-measure such lists.
   The prover REFUTED the first phase offset (depth 15): `advance` is only CONDITIONALLY
   strict, so `lambdef`'s leading `advance` does NOT pay for a rise. Depth 9 proves.
   Lesson (bm).
2. **`_pattern_number` CONVERTED (514 -> 513)** — the [MODEL] boundary on the `Constant`
   NUMBER arm. **CENSUS-FIRST PAID**: the model needed already existed and is CERTIFIED —
   `pyconst_val` (7 arms, axiom-free Phase2c_PyConstVal.v / PyConstVal.lean). Relaunch
   #11's bespoke two-arm `irconst` is **RETIRED**, not extended. The key is a
   count-neutral RETURN INTERFACE: `_parse_number` stays `\trusted` but gains
   `-> "PyConstVal"`, so its `val` goes from `(s: int) : unit` to an UNINTERPRETED
   `(s: string) : pyconst_val`. Lesson (bn).
3. **`atom` REFUTED — [NO-ADVANCE VARIANT CYCLE]**, every VALUE piece measured working.
4. **`closed_pattern` REFUTED — [FOUR NAMED GAPS]**, and its own earlier re-diagnosis
   CORRECTED by bisection (see the warning below).

## THE WARNING THIS SESSION EARNED — bisect a refutation before recording it

The first `closed_pattern` refutation named "tuple membership defeats the string
classifier" as its headline gap. A **two-line probe disproved it in one second.** A wrong
capability name is worse than "blocked": the whole value of the naming discipline — three
boundaries reopened the same day across two sessions — is that the next worker BUILDS the
named thing. Probe each named cause in isolation before you write it down.

## Pick up here — in this order

1. **`atom` — ONE capability, named, TCB-FREE, and it is the cleanest item on the board.**
   Every VALUE piece is measured working (`PVBool true/false` for True/False — not
   `PVInt 1`; `PVEllipsis` for `...` via an additive `py_ellipsis` marker; the number arm;
   `Name`; `strings` with a `-> "ExprIR"` interface). The blocker is purely TERMINATION:
   converting `atom` removes the abstract `val` that CUTS the expression `let rec` group,
   19 members become 28, and the no-advance edges form a genuine CYCLE
   `atom -> yield_expr -> testlist -> test -> or_test -> … -> unary_postfix -> atom`.
   **THE FIX: a token-kind PRECONDITION on `yield_expr` / `atom_paren` / `atom_list` /
   `atom_brace` / `_dict_rest`** (`#@ requires self.toks[self.i].type == _tokenize.OP`, or
   `== NAME` for `yield_expr`). Each opens by consuming a token its CALLER has just tested,
   so the evidence exists and is merely in the wrong function; the precondition is
   DISCHARGEABLE at every call site from the `ensures \result != False ==>
   self.toks[self.i].type == …` clauses `at_op`/`at_kw` ALREADY export, and inside the
   callee it composes with the EOF-sentinel invariant exactly as `_name_str`'s strictness
   proof does. That makes each leading `advance` provably strict, PAYS the outgoing edges,
   and cuts the cycle. **A precondition is a proof obligation at the call site, not an
   assumption — no new `\trusted` surface, no axiom.** Then re-derive all 28 offsets and
   price the SHAPE on the 1-second oracle before spending a proof.
2. **`closed_pattern` — FOUR gaps, two already BUILT AND MEASURED** (`MatchValue` as
   `IrPyMatchValue emit_ir`; `MatchAs`'s slots `emit_ir`/`string` -> `iropt_ir`/`iropt_str`,
   which is the reopening capability the ctor table's own note had recorded). Remaining:
   (3) the const-dict lowering extended from a MODULE-LEVEL table to an INLINE dict
   literal indexed by a local; (4) the `s = t.string` INT-ERASURE, which is a JOIN over
   several uses — NOT the tuple membership, NOT the dict index alone, NOT `MatchAs` (all
   three disproved by probe).
3. **The two Module5 dispatchers — 142 of the 176 shadowed sites** (`_csl_to_ir` 92,
   `_py_expr_to_ir` 44, `_py_op_to_str` 6). The recorded L2 TYPE-UNIFICATION wall and the
   biggest remaining lever on the shadowed metric. "`comprehension` joins the family" is
   the named shape. A large, well-defined, funded-window build.
4. **`small_stmt`** — [HETEROGENEOUS CONVERTED RETURNS]. Note that `arg` and `comprehension`
   joining the family are now well-trodden, so migrating the six siblings onto
   `_PYAST_IRNODE_CTORS` arms (plus `alias`) is mechanical — but the count does not move
   until the LAST one lands, so it is 1 marker for a big build.
5. **`strings`** — the last f-string-cluster member and the hardest: `b"".join(...)` over a
   BYTES value, a `kinds` SET, and a list of 4-TUPLES. Not probed.

## RECORDED BOUNDARIES — do not re-grind without the named capability

- **`atom` — [NO-ADVANCE VARIANT CYCLE].** Ladder 1; capability named above.
- **`closed_pattern` — [FOUR NAMED GAPS].** Ladder 2; two built and measured.
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER], a JUDGEMENT not a wall (lesson
  (bd)).** Proved and reverted anyway: they trade a COUNTED marker for an UNCOUNTED
  erasure-ledger entry. Reopening: an `emit_ir` that CARRIES the four ASDL location attrs.
- **`_set_ctx(node, _N("Store")())` — [CORRECTNESS].** Blocks `namedexpr_test`,
  `_comp_target`, `_for_target`, `expr_stmt`, `del_stmt`, `_with_item`. Reopening: a
  functional `set_ctx` in the LIVE SOURCE. POSITION is NOT part of this (lesson (az)).
- **`node(self, name, start_tok, **kw)` — [MODEL].** A `**kw` SPLAT into `_N(name)(…)`
  with a run-time class name.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].** Ladder 3.
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~51 stubs)** — `self.interleave(lambda: …)` (LAMBDA +
  higher-order) and `with self.delimit(…)`. A fundamental modelling boundary.
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.

## FLAGGED FOR THE USER (outside the campaign's mandate — NOT taken)

- **The Alt-Ergo pin at `pycsl.py:1318` is stale** (2.6.2 vs installed 2.6.3), so a
  nominally dual-prover run is silently Z3-only. Keep passing
  `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
- **`_py_stmt_assign` reads `stmt.targets[0]` only** — chained-assignment targets silently
  dropped. Repair measured corpus-byte-inert and reverted: the mirror's own model reads
  through `assign_target0_ast`, so the fix emits BYTE-IDENTICALLY (lesson (bk) §2).
  Reopening: `assign_targets_len` / `assign_targetk_ast` in the reader model.
- **NEW: `_py_expr_constant` lowers the `...` literal to the INTEGER ZERO.** A silent
  wrong-value erasure. Left alone deliberately — giving `...` a real IR node type would
  turn a silent 0 into a hard compile error for any program using `...` in an expression.
  The zero-blast-radius repair WAS built and measured (an ADDITIVE `py_ellipsis` marker key
  no existing consumer can observe, so corpus byte-diff 0 BY CONSTRUCTION) and reverted
  with `atom`, its only consumer.
- Still standing: dropping the `_record_array_fields` PROXY disjunct from
  `_handle_dotted_call`'s concrete-sibling gate changes 6 of 813 corpus files, each
  replacing an opaque abstract `val` with the real concrete application (lesson (bc)).

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. **A `pycsl.py` run has TWO phases and the second dominates.** The prover phase streams
   `Prover result is:` lines; the POST-PROOF NON-VACUITY phase then spawns one `why3` per
   goal over `/tmp/.pycsl_vac_*.mlw` and prints nothing until it finishes. `pure_ast` is
   ~5 min of proving and ~40 min of non-vacuity. **A FAILING run is much FASTER than a
   passing one** (it short-circuits) — do not read a quick finish as good news.
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** A `run_in_background` poller
   will never wake you. Either WIP-commit and wait for the battery in the FOREGROUND of
   your turn (`timeout 570 bash -c 'until grep -q ALLDONE …; do sleep 10; done'`, repeated),
   or stop cleanly and SAY the proof is pending so the handoff names it.
9. **`scratchpad/w2/proveseq.sh <logdir> <files…>`** proves a LIST sequentially (obeys
   lesson (ai) by construction). **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all
   52 mirrors WITH L3-tc and writes an md5+TC_OK/TC_FAIL manifest in ~35 s — diff two
   manifests for the exact changed-mirror set. `bin/byte-diff-sweep.sh <out>` does the 813
   corpus files in ~32 s. Keep a HEAD worktree at
   `…/8f7f6044-…/scratchpad/head-wt` for baselines.
10. **`--fun` CANNOT probe a mutual-recursion group.** A group is proved whole or not at all.
11. **`bin/check-shadowed-selfcalls.py` has its BASELINE as a constant in the file.**

## THE FASTEST THING THIS CAMPAIGN KNOWS — use it

**An emit-only run is a ~1.5-SECOND oracle for pure_ast.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON) and leaves the `.mlw` for inspection. It prices a
VARIANT SHAPE for free ("All functions in a recursive definition must use the same
well-founded order" is a TYPE-CHECK error) but NOT the decrease. It is also how a
refutation gets BISECTED: two of this session's four `closed_pattern` gaps were disproved by
one-second probes, and one of them had already been written down as fact.

**Run `bin/check-self-annotate-sync.sh` immediately after ANY live-emitter edit** — seconds,
and it catches an edit that landed in an UN-TRUSTED mirror body before it costs proof time.
That happened this session: the change's natural home was `_compute_return_type`, whose
mirror is un-trusted, so it was PORTED and `module6_whyml/functions` re-proved (lesson (vv)
obeyed, not dodged).

## Method notes this session paid for (full text in wall-lessons.md, (bm)-(bn))

- **(bm)** an element type is a FIXPOINT over the assignment graph, not a property of one
  site; an optional local can be optional WITHOUT reaching an optional slot, and
  PRESENCE-TESTING is the observability criterion; a carrier appended to a carrier seq
  COPIES while appended to a plain list it PROJECTS — the DESTINATION decides; and
  `advance` is only CONDITIONALLY strict, so a new group member whose incoming edge is a
  bare `advance` must sit strictly BELOW its caller.
- **(bn)** CENSUS before building a carrier (a carrier you invented last session is not
  evidence that no model exists); a RETURN INTERFACE is the cheapest modelling lever and
  costs no marker, and an UNINTERPRETED function is the honest abstraction for a
  multi-shaped result; RENAMING A SLOT TYPE IS CROSS-CUTTING — one stale comparison put
  `if true then` back into a method converted last session to remove exactly that defect;
  and a NO-ADVANCE CYCLE is not a bad offset but a different wall.
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit TWICE in one increment this session
  (declaration vs call-site return types; and the retired slot name); **(ai)** never stack
  whole-file proofs; **(bl)** grep the emitted body for `if true then` / `&& false` after
  ANY slot-type change, not only after a conversion; **(az)/(bd)** revert dead capability
  with its spike.

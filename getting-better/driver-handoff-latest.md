# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-29, RELAUNCH #13 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 508 · grep-substring 533 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep
  hits are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25. Stable across
  three samples.
  **Window #2 delta so far: markers 530 -> 508, grep 555 -> 533.**
  **This session (#13): 513 -> 508 — FIVE conversions in three gated increments, one
  measured CERTIFIED-BOUNDARY, one gate blind spot repaired, and one live-tool defect
  found and fixed.**
- **`bin/check-shadowed-selfcalls.py`: 27 CONVERTED methods / 176 bypassing call sites,
  ratchet 27** — unchanged. Needs `TMPDIR` on the repo filesystem
  (`TMPDIR=/home/fabrice/git/pycsl/scratchpad`).
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**. Literal-guard grep: **0**.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **802 / 785 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**. Corpus byte-diff **0 over 813/813**.
  `frontend/pure_ast` proves **2552 / 2552**. `bin/self-annotate-mirror-check.sh`
  byte-identical to the HEAD baseline.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Commits unpushed by design.

## WHAT THIS SESSION LANDED

1. **`atom` CONVERTED (513 -> 512)** — the [NO-ADVANCE VARIANT CYCLE] boundary, broken by
   exactly the capability its own refutation named: a **token-kind PRECONDITION**
   (`#@ requires self.toks[self.i].type == _tokenize.OP`, `== NAME` for `yield_expr`) on the
   five methods whose leading `advance` consumes a token the caller already tested.
   Discharged at every call site from `at_op`/`at_kw`'s existing `ensures`; ZERO new
   `\trusted` surface, no axiom. The expression group went 21 -> 28 members and was
   RE-DEPTHED (offsets 0..15, multiplier 16 unchanged).
2. **`closed_pattern` CONVERTED (512 -> 511)** — all FOUR recorded gaps plus a FIFTH the
   earlier bisection had missed (`MatchClass` had no ctor entry either). New capabilities:
   an INLINE const-dict -> `pyconst_val` projection; an empty list literal admitted into a
   `seq string` slot as `Seq.empty`; a string-returning CALL admitted into an `iropt_str`
   slot.
3. **`_with_item` + `_for_target` + `_comp_target` CONVERTED (511 -> 508)** — the
   [CORRECTNESS] boundary on `_set_ctx`, broken by a **RETURN INTERFACE on a stub that
   stays `\trusted`**. THREE markers for ONE capability.
4. **`strings` PROBED for the first time** and recorded as
   CERTIFIED-BOUNDARY [HETEROGENEOUS TUPLE ELEMENT TYPE] — a COST/SCALE boundary.
5. **A GATE BLIND SPOT REPAIRED**: `bin/check-emitted-vacuity.py` parsed only `  let …`
   heads, so every `with` CONTINUATION of every mutual-recursion group was invisible —
   531 of 3839 emitted functions, 14% of the surface, unchecked for the whole campaign.
   Widened; finds no new erasure anywhere, a pure tightening.
6. **A LIVE-TOOL DEFECT FOUND AND FIXED**: `_record_field_elem_locals` was published only
   AFTER `_typed_local_vars`, so string classification of a `<record>.field` read used the
   PREVIOUS function's map — **emission-order-dependent typing**. See lesson (bp).

## THE TWO THINGS THIS SESSION PROVES ABOUT METHOD

- **A named reopening capability is worth more than a conversion.** Three recorded
  boundaries fell this session, each to the capability its own refutation had named. Keep
  naming them precisely, and keep BISECTING before recording (lesson (bp) §2: when a
  source-level bisection cannot isolate a cause, stop cutting the source and INSTRUMENT
  THE DECISION — printing the classifier's own inputs for two sibling functions named the
  culprit in one run, after a source bisection had convicted an innocent).
- **A gate reporting unearned GOOD news is a bug report about the gate** (lesson (bo) §3).
  The vacuity blind spot surfaced only because a long-known erasure was suddenly declared
  fixed by a change that could not possibly have fixed it.

## Pick up here — in this order

1. **`namedexpr_test` — FULLY ANALYSED, NOT TAKEN, and it is the cheapest item on the
   board.** The live `_set_ctx` call site change was built and REVERTED as dead capability
   (one line to redo: `first = _set_ctx(first, _N("Store")())` at `pure_ast.py:1573`).
   Two things are needed beyond that: (a) a NEW `_PYAST_IRNODE_CTORS` entry
   `"NamedExpr": ("IrPyNamedExpr", [("target", "emit_ir"), ("value", "emit_ir")])` — the
   EXISTING `IrNamedExpr string emit_ir` is the CSL-side ctor and types the target as a
   STRING, so it cannot be reused; (b) a RE-DEPTHING: `namedexpr_test` must sit strictly
   ABOVE `test` (12, which it reaches without advancing) and strictly BELOW both
   `test_or_star` and `_call_args` (which reach it without advancing), so it takes 13 and
   those two move 0 -> 14 and 13 -> 14 respectively. Checked: nothing else collides at 14,
   and every rise into 14 is paid by one strict `advance` (14 < 16).
2. **`expr_stmt` and `del_stmt`** — the remaining two of the six `_set_ctx`-blocked stubs.
   Their `_set_ctx` sites are `pure_ast.py:988/996` (`first`) and `:897/1006` (`tg`, a LOOP
   VARIABLE — assigning to a loop variable does NOT propagate into the list, so those two
   sites need `elts[i] = _set_ctx(elts[i], …)` or an equivalent, which is a REAL live
   change, not a runtime-identical one; measure the corpus byte-diff carefully).
3. **The two Module5 dispatchers — 142 of the 176 shadowed sites** (`_csl_to_ir` 92,
   `_py_expr_to_ir` 44, `_py_op_to_str` 6). The recorded L2 TYPE-UNIFICATION wall and the
   biggest remaining lever on the shadowed metric. "`comprehension` joins the family" is
   the named shape. A large, well-defined, funded-window build.
4. **`small_stmt`** — [HETEROGENEOUS CONVERTED RETURNS]. `arg`, `comprehension`, `withitem`
   and the Match family joining `_PYAST_IRNODE_CTORS` are now well-trodden, so migrating
   the six siblings (plus `alias`) is mechanical — but the count does not move until the
   LAST one lands, so it is 1 marker for a big build.
5. **`strings`** — CERTIFIED-BOUNDARY [HETEROGENEOUS TUPLE ELEMENT TYPE], five capabilities
   for one marker; see the full measured gap list on the stub itself.

## RECORDED BOUNDARIES — do not re-grind without the named capability

- **`strings` — [HETEROGENEOUS TUPLE ELEMENT TYPE]**, measured this session. `parts` is a
  seq of 4-TUPLES that collapses to a HASH CONSTANT; its three consumers (a destructuring
  `for`, a genexp fold over a slot projection through the UNBOUND `subscript_get`, and a
  `join` over a slot projection) each need their own capability, and `b"".join` vs
  `"".join` emit the IDENTICAL `join_1 0`. **The `kinds` SET is NOT a gap** — it models
  cleanly as `map string (option int)`; the old record had guessed wrong.
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER], a JUDGEMENT not a wall (lesson
  (bd)).** Reopening: an `emit_ir` that CARRIES the four ASDL location attrs.
- **`node(self, name, start_tok, **kw)` — [MODEL].** A `**kw` SPLAT into `_N(name)(…)`
  with a run-time class name.
- **`_slice`** — needs `self._lines`, a `List[str]` field the mirror's `__init__` does not
  model. Not probed further.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].** Ladder 3.
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~51 stubs)** — `self.interleave(lambda: …)` and
  `with self.delimit(…)`. A fundamental modelling boundary.
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.

## FLAGGED FOR THE USER (outside the campaign's mandate — NOT taken)

- **The Alt-Ergo pin at `pycsl.py:1318` is stale** (2.6.2 vs installed 2.6.3), so a
  nominally dual-prover run is silently Z3-only. Keep passing
  `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
- **`_py_stmt_assign` reads `stmt.targets[0]` only** — chained-assignment targets silently
  dropped. Repair measured corpus-byte-inert and reverted (lesson (bk) §2). Reopening:
  `assign_targets_len` / `assign_targetk_ast` in the reader model.
- Still standing: dropping the `_record_array_fields` PROXY disjunct from
  `_handle_dotted_call`'s concrete-sibling gate changes 6 of 813 corpus files (lesson (bc)).

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. **A `pycsl.py` run has TWO phases and the second dominates.** `pure_ast` is now ~7 min of
   proving and ~38 min of non-vacuity. **A FAILING run is much FASTER than a passing one.**
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** Wait in the FOREGROUND with a
   repeated `timeout 560 bash -c 'until grep -q ALLDONE …; do sleep 15; done'`, or WIP-commit
   and stop cleanly SAYING the proof is pending. Both worked cleanly this session.
9. **`scratchpad/w2/proveseq.sh <logdir> <files…>`** proves a LIST sequentially (lesson (ai)
   by construction). **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors
   WITH L3-tc and writes `manifest.md5` (note: `.md5`, not `manifest.txt`) in ~35 s.
   `bin/byte-diff-sweep.sh <out>` does the 813 corpus files in ~32 s. Keep a HEAD worktree
   at `…/8f7f6044-…/scratchpad/head-wt`; refresh it with
   `git fetch /home/fabrice/git/pycsl <branch> && git checkout -q FETCH_HEAD`.
10. **`--fun` CANNOT probe a mutual-recursion group.** A group is proved whole or not at all.
11. **`bin/check-shadowed-selfcalls.py` has its BASELINE as a constant in the file.**

## THE FASTEST THINGS THIS CAMPAIGN KNOWS — use them

**An emit-only run is a ~10-SECOND oracle for pure_ast.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON) and leaves the `.mlw`. It prices a VARIANT SHAPE for
free ("All functions in a recursive definition must use the same well-founded order" is a
TYPE-CHECK error) but NOT the decrease, and it is how a refutation gets BISECTED. **Run it
after EVERY slot-type edit, not at the end** — retyping `MatchAs` broke `pattern`, converted
sessions ago, and the oracle caught it in one second.

**`bin/byte-diff-sweep.sh` is a 32-second check on a LIVE-SOURCE edit.** Two live edits
landed this session and both were confirmed runtime-inert by 0 differing bytes over 813
files, BEFORE spending 45 minutes on a proof.

**Run `bin/check-self-annotate-sync.sh` immediately after ANY live-emitter edit** — seconds,
and it catches an edit whose natural home is an UN-TRUSTED mirror body (it fired once this
session on `_py_expr_constant`; the port turned out to be emission-BYTE-IDENTICAL, so no
re-proof was owed).

## Method notes this session paid for (full text in wall-lessons.md, (bo)-(bq))

- **(bo)** a PRECONDITION moves strictness evidence from the caller, where it is already
  proved, into the callee, where it is needed — free, no TCB; re-depthing is the real work
  and an old numbering can be IMPOSSIBLE rather than merely bad, so derive the whole
  assignment and check the maximum rise against the multiplier BEFORE proving; and a gate
  reporting unearned good news is a bug report about the gate.
- **(bp)** a per-function map read one function EARLY is not stale data, it is a different
  function's data, and it makes emitted typing EMISSION-ORDER-DEPENDENT; when a source
  bisection cannot isolate a cause, INSTRUMENT THE DECISION instead; a gap list written from
  one measurement misses the slot that never got its turn (the emitter stops at the first
  decline); and sibling slot kinds must agree about the same placeholder literal.
- **(bq)** a returnless MUTATOR is modelled as a NO-OP, which is a confidently FALSE value,
  not a coarse one — the fix is a RETURN INTERFACE (runtime-identical, checkable by the
  corpus byte-diff), which is now the third such win in two sessions and the cheapest lever
  on the board; and revert the call sites you cannot yet consume.
- Still live: **(am)** ASSUME TWO PRODUCERS; **(ai)** never stack whole-file proofs;
  **(bl)** grep the emitted body for `if true then` / `&& false` after ANY slot-type change;
  **(az)/(bd)** revert dead capability with its spike; **(bn)** a slot-type rename or
  retype is CROSS-CUTTING.

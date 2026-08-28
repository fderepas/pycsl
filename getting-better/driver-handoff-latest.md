# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-28, RELAUNCH #10 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 521 · grep-substring 546 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep hits
  are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  **Window #2 delta so far: markers 530 -> 521, grep 555 -> 546 — NINE conversions,
  a 18-method faithfulness repair, TWO certified boundaries, in nine gated increments.**
- **`bin/check-shadowed-selfcalls.py`: 32 CONVERTED methods / 192 bypassing call sites,
  RATCHET now 32** (was 50 / 259 at window start). Run it every increment; it needs
  `TMPDIR` on the repo filesystem (`TMPDIR=/home/fabrice/git/pycsl/scratchpad`).
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**, unchanged.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **789 / 772 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known** (up one — see `_dict_rest` below),
  0 input-blind. Corpus byte-diff **0 over 813/813**. `bin/self-annotate-mirror-check.sh`
  byte-identical to the HEAD baseline (3 mirrors with pre-existing mirror-only defs — the
  standing baseline, not new drift).
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, `.lia.cache`/`.vo`
  artifacts, untracked `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Unpushed commits are
  deliberate. **~81 h remained on the window at handoff time.**

## WHAT THIS WINDOW LANDED (nine gated increments + three lesson commits)

1. **`trailers` + `classdef` CONVERTED** (530 -> 528). All four named `trailers` pieces in
   ONE increment. `classdef`'s recorded [VALUE MODEL] boundary named exactly the piece
   (iii)/(iv) capability as its reopening condition, so it came out with it.
2. **Shadowed-selfcall repair wave 1** (50 -> 43 methods, 259 -> 217 sites).
3. **Shadowed-selfcall repair wave 2** (43 -> 35, 217 -> 208).
4. **`_line_ends_with_colon` CONVERTED** (528 -> 527). BREAKS lesson (ba).
5. **Shadowed-selfcall repair wave 3** (35 -> 32, 208 -> 192). Built the
   `Optional[str]`-return call-site unwrap that unblocked `_field_type_of` (14 sites).
6. **`global_stmt` CONVERTED** (527 -> 526); **`_fin` REFUTED** [ERASURE-LEDGER], lesson (bd).
7. **`_call_args` CONVERTED** (526 -> 525) — and it RETIRES the one assumed clause
   increment 1 added. TCB net NEGATIVE.
8. **`atom_list` + `atom_paren` CONVERTED** (525 -> 523).
9. **`atom_brace` + `_dict_rest` CONVERTED** (523 -> 521). NEW `iroptlist` carrier.

New emit_ir arms this window: **fifty-two total** (was thirty-seven). Added: `IrPyCall`,
`IrPySubscript`, `IrPyClassDef`, `IrPyGlobal (seq string)`, `IrPyNonlocal (seq string)`,
`IrPyKeyword iropt_str emit_ir`, `IrPyComprehension`, `IrPyGeneratorExp`, `IrPyList`,
`IrPyListComp`, `IrPySet`, `IrPySetComp`, `IrPyDictComp`, `IrPyDict iroptlist irlist`.

## Pick up here — in this order

1. **The shadowed residue is 32 methods / 192 sites, and 142 of those sites are TWO
   Module5 dispatchers** (`_csl_to_ir` 92, `_py_expr_to_ir` 44, `_py_op_to_str` 6). Those
   are the recorded L2 TYPE-UNIFICATION wall (the dispatcher is `emit_ir -> emit_ir` while
   each of its 21+ handlers takes a DIFFERENT RECORD type). **The `comprehension`-joins-the-
   family move this window is the shape that answers it**: give every handler's input class
   an `_PYAST_IRNODE_CTORS`-style ADT arm so the handlers unify on `emit_ir`. That is a
   large, well-defined build and a funded window is the budget for it. Everything else in
   the residue is a long tail whose per-method blocker is NAMED in the increment-5 commit
   message (union-vs-value at the call site, self-recursion needing a `\variant`,
   `@staticmethod` — fail-closed and correct, arity-0 `-> None` bridges, `option (string,
   hval-map)` tuple returns).
2. **`small_stmt`** — still [HETEROGENEOUS CONVERTED RETURNS]. The five siblings
   (`return_stmt`, `raise_stmt`, `assert_stmt`, `import_stmt`, `import_from`) are CONVERTED
   onto harvested RECORD returns; migrating them onto `_PYAST_IRNODE_CTORS` arms (plus
   `alias`) is now a WELL-TRODDEN move — this window did exactly that for `comprehension`.
   The count does not move until the LAST one lands.
3. **The `strings` / `_fstring*` cluster** (7 stubs) — not yet probed this window.
4. **`_binop`** [RECOGNIZER] — `_BINOP` is a const dict of TUPLES destructured into two
   locals, then `_N(opname)()` on a LOCAL. The variable-class-name family now has THREE
   forms built (literal, ternary local, **formal parameter** — new this window); the LOCAL
   form bound from a const-dict TUPLE is the fourth and it is the last one `_binop` needs.

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_fin` — [ERASURE-LEDGER], and this one is a JUDGEMENT, not a wall (lesson (bd)).**
  The full spike was BUILT and proved 1612/1612; it was reverted because
  `check-emitted-vacuity --emit` then reports `_parser___fin erased=['start_tok']`, and the
  conversion would trade a COUNTED `\trusted` marker for an UNCOUNTED ledger entry while
  buying nothing (every call site already elides `_fin`). Reopening: an `emit_ir` that
  CARRIES the four ASDL location attributes as payload. Both spike-only emitter capabilities
  were reverted with it. **Do not re-spike it** — read lesson (bd) and (bf) §3 first, which
  give the sharpened test (`what would a CALLER gain?`) that also explains why the twin
  `_dict_rest` WAS admitted.
- **`_set_ctx(node, _N("Store")())` — [CORRECTNESS].** `emit_ir` is IMMUTABLE and `ctx` IS
  modelled. Blocks `namedexpr_test`, `_comp_target`, `_for_target`, `expr_stmt`, `del_stmt`,
  `_with_item`. Reopening: a functional `set_ctx` in the LIVE SOURCE. The POSITION plane is
  NOT part of this (lesson (az)) — only `ctx`.
- **`small_stmt` — [HETEROGENEOUS CONVERTED RETURNS]** (lessons (av)-(ax)). See ladder #2.
- **`_subscript_item` — [MODEL].** Flow-sensitive narrowing (`lower = upper = step = None`
  then `return lower` in an emit_ir position). The `Optional[<record>]` LOCAL carrier built
  this window does NOT cover it: this is a chained assignment returning an
  `Optional[emit_ir]` local in an emit_ir return position.
- **`_pattern_number`, `atom`, `closed_pattern` — [MODEL].** `Constant(value=…)` needs the
  parser's own number/constant classification.
- **`_binop` — [RECOGNIZER].** See ladder #4.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].** See
  ladder #1.
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~60 stubs)** is blocked by `self.interleave(lambda: …,
  self.traverse, node.names)` — LAMBDA + higher-order function — and `with self.delimit(…)`
  context managers. A fundamental modelling boundary, not a cost one.
- **`error` / `unsupported`** stay `\trusted` by design (raise + f-string); count-neutral.

## FLAGGED FOR THE USER (outside the campaign's mandate — NOT taken)

**Dropping the `_record_array_fields` PROXY disjunct from `_handle_dotted_call`'s
concrete-sibling gate changes only 6 of 813 corpus files, and every one of those six
replaces an opaque abstract `val` with the real concrete application** — including `0721`
and `0722`, where the abstract route had SILENTLY DROPPED the callee's
`requires self.session_authenticated = 1`. That is a genuine faithfulness hole in the LIVE
TOOL, but fixing it changes emission for USERS, not just the mirror, so this campaign used
the other route (mark the callees with `#@ sibling_concrete`, corpus byte-inert by
construction). Measured, reverted, recorded in lesson (bc).

Also still flagged from earlier windows: **the Alt-Ergo pin at `pycsl.py:1318` is stale**
(2.6.2 vs installed 2.6.3), so a nominally dual-prover run is silently Z3-only. Keep passing
`--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.

## Instrument facts (re-verified this window)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files; `--keep-mlw`
   writes `<source>.mlw` NEXT TO THE SOURCE.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. A HEAD worktree has no `.venv` and `bin/byte-diff-sweep.sh` uses `$ROOT/.venv/bin/python3`:
   `ln -sfn <repo>/.venv <worktree>/.venv` first, or the sweep emits ZERO files and the diff
   still reports 0.
7. `python3 -u` on every proof, or the log stays empty until the run ends.
8. The Bash tool caps a foreground command at 10 minutes. Run the proof with `nohup … &` and
   WAIT with an `until ! kill -0 <pid>; do sleep 60; done` loop. **`scratchpad/w2/proveseq.sh`
   (written this window) proves a LIST of mirrors sequentially and appends a
   START/DONE/valid/total line per file to `<logdir>/seq.status`** — poll that instead of
   babysitting each run. It obeys lesson (ai) by construction.
9. **`scratchpad/w2/sweep.sh <repo-root> <outdir>` emits all 52 mirrors WITH L3-tc and writes
   an md5+TC_OK/TC_FAIL manifest — it takes ~35 SECONDS, not the ~13 min the old handoff
   claimed.** Diff two manifests to get the exact changed-mirror set; that is how the
   SECOND-ORDER blast radius (a mixin change re-emitting `Module6_WhyMLTranspiler` and
   `pycsl`) was found rather than guessed.

## THE FASTEST THING THIS CAMPAIGN KNOWS — use it

**An emit-only run is a 1-SECOND oracle for pure_ast.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON) and leaves the `.mlw` for inspection. EVERY capability
this window was designed by porting a body, emitting, READING the emitted WhyML for facades,
and iterating — before spending a minute of proof time. The `#@ sibling_concrete` triage
(26 markers tried, 15 effective) is a 26 × 1-second loop.

**And run `bin/check-self-annotate-sync.sh` immediately after ANY live-emitter edit.** It
costs seconds and it caught two mis-placed edits this window before either cost proof time
(lesson (bb)).

## The §10.4 RE-PORT PRICE LIST (re-measured this window)

| mirror | goals | wall clock |
|---|---|---|
| any `\trusted` mirror body | — | **0** |
| `module6_whyml/expr_ghost_collections` | 166 | ~2 min |
| `module6_whyml/types` | 659 | ~13 min |
| `Module6_WhyMLTranspiler` | 706 | ~12 min |
| `pycsl` | 730 | ~16 min |
| `module6_whyml/statements` | **894** | ~22 min |
| `module6_whyml/expressions` | 1023 | ~25 min |
| `frontend/Module5_IREmitter` | 1114 | ~50 min |
| `module6_whyml/functions` | 1177 | ~32 min |
| `module6_whyml/stmt_control_flow` | 1832 | ~42 min |
| `frontend/pure_ast` | **1868** (was 1520) | ~35 min |

Mirror emission sweep WITH L3-tc (52 files): **~35 s**. Corpus byte-diff sweep (813 files,
`--no-typecheck`, 6 jobs): **~32 s**.

## Method notes this window paid for (full text in wall-lessons.md, (bb)-(bf))

- **(bb)** a change's HOME is decided by the mirror's FIDELITY obligation, not by where it
  logically belongs. `_refine_tuple_return_type` is called by BOTH return-type producers, so
  ONE insertion there paid lesson (am)'s two-producer trap once and touched ONE converted
  mirror body instead of two. And the mirror body must be EMITTABLE, not merely equal.
- **(bc)** the shadowed-selfcall gate is fixed by MARKING CALLEES (`#@ sibling_concrete`),
  via a cumulative per-file triage on the 1-second emit oracle; the proxy-gate corpus
  measurement is a finding in its own right (see FLAGGED FOR THE USER). Four named reasons a
  marker cannot fire.
- **(bd)** DECLINE a conversion that moves a hole from a COUNTED register to an UNCOUNTED
  one. Revert the spike's capabilities WITH it.
- **(be)** a class name chosen at RUN TIME lowers to a dispatch DERIVED FROM THE TABLE with
  an EXACT tail (`kind_of (IrOther k) = k`).
- **(bf)** a list of harvested RECORDS cannot be a payload (`seq <record>` inside `emit_ir`
  is non-strictly-positive) — the class must JOIN the family; a list with `None` ELEMENTS
  needs its own `iroptlist` carrier; and the SHARPENED erasure-ledger test: *what would a
  CALLER gain?*
- Still live: **(am)** ASSUME TWO PRODUCERS — it bit again on the tuple return-type and on
  the tuple concrete-sibling allowlist; **(ai)** never stack whole-file proofs (obeyed
  throughout — `scratchpad/w2/proveseq.sh` enforces it); **(ay)** run BOTH
  untrusted-emitted and shadowed-selfcalls every increment.

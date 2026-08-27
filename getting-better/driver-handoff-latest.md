# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #7 worker)

## State, verified from the surface

- **Count: MARKERS 542 · grep-substring 567 · offset 25 · unattached 0.** Quote BOTH.
  Get them from **`bin/count-trusted-directives.py`**, never a hand-rolled grep — the grep figure
  counts SUBSTRING hits and 25 of them are one boilerplate module-docstring line repeated across
  25 mirror files.
  **Window delta: markers 549 -> 542, grep 574 -> 567 — SEVEN conversions in four gated
  increments**, plus two clean refutations that landed nothing.
- Ledger **3**, untouched. No new axiom. Every bridge used is a pre-existing `val` with pointwise
  postconditions (`snapshot`, `seq_to_irlist`, `materialize_emit_ir`).
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **768 / 751 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, 0 input-blind. Corpus byte-diff **0 over 813/813**.
  `bin/self-annotate-mirror-check.sh` reports **3 pre-existing** mirror-only defs in
  `ControlFlowStmtMixin` — that is the standing baseline, not new drift.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache`, untracked `scratchpad/`, `prompt.txt`, the rocq `.vo`
  artifacts). Leave it alone. `getting-better/.driver-deadline` intact.

## WHAT THIS WINDOW CONVERTED (all in `frontend/pure_ast.py`)

`exprlist` · `_looks_like_match` · `statement` · `block` · `parse_module` · `case_block` ·
`match_stmt`.

`statement` and `block` are the structural ones: every compound-statement parser calls `block`,
and `block` now carries a REAL `seq emit_ir` statement list instead of the opaque `body_extend_1`
facade it had before.

## THE FOUR CAPABILITIES BUILT — all of them general, re-census against them

1. **The `-> bool` PREDICATE TWIN.** A `\trusted` stub declared `-> bool` now types as `int`
   (0/1 — the file's own convention, see lesson (an)), in BOTH producers:
   `functions._compute_return_type` (the stub's own `val`) and
   `functions._build_method_return_type_map` (the `self.<m>()` CALL SITE). **This refutes the
   previous handoff's "blocker 4".** `_compute_return_type` IS the decision point; the earlier
   null measurement had no `-> bool` annotation on the stub at all AND was reading the other
   producer's output. Lesson (am).
2. **The `.extend` SEQ ACCUMULATOR.** `body = []` + `body.extend(<call returning array emit_ir>)`
   is now a `seq emit_ir` local grown by `Seq.(++) !body (snapshot <arr>)`.
   `_collect_array_elem_types` structurally cannot see such a local (its first assignment is an
   EMPTY list literal, which carries no element type), so the promotion is a dedicated pass in
   `_typed_local_vars`. Both halves are in `\trusted` mirrors → §10.4 cost 0.
3. **The EMPTY-LIST PLACEHOLDER, handled in three places.** `[]` lowers to `(Array.make 1024 0)`
   — a 1024-long ZERO array, not an empty one (lesson (ao)). It is now (a) excluded from
   `_handle_dotted_call`'s array-shape param inference, (b) coerced to the int witness for an
   int-erased param, and (c) bound as the genuinely empty `ILNil` in an `irlist` payload slot.
   All three gated on the exact placeholder literal.
4. **The GAP-FREE-PREFIX keyword binder** (lesson (ap)). The increment-13 binder only applied when
   it could fill EVERY formal, so `self.funcdef([], async_=False)` fell back to the partial
   application it was written to prevent. It now accepts any gap-free prefix that covers every
   keyword, and `_handle_dotted_call`'s R7 default fill completes the tail.

Four new `_PYAST_IRNODE_CTORS` arms: `IrPyModule irlist irlist`,
`IrPyMatchCase emit_ir iropt_ir irlist`, `IrPyMatch emit_ir irlist`. (Nineteen arms total.)

## TCB ADDED THIS WINDOW — know exactly what it is

Nine `-> "ExprIR"` RETURN INTERFACES and, on the same nine trusted statement-producing stubs
(`for_stmt`, `with_stmt`, `try_stmt`, `funcdef`, `classdef`, `async_stmt`, `decorated`,
`match_stmt`, `type_alias_stmt`) plus `small_stmt`, a cursor clause **`ensures self.i >
\old(self.i)`** (STRICT, not the usual `>=`). All of them are consumed — `statement` needs the
interfaces, `block`'s loop VARIANT needs the strictness — and the FIRST proof attempt measured
their absence exactly (880 Valid / 22 non-Valid, every failure `_parser__statement'vc`'s cursor
postcondition). Each becomes a PROOF the day its stub converts. Four converted members of the same
chain (`if_stmt`, `while_stmt`, `simple_stmt`, `statement`) now PROVE strict progress.

Two runtime-INERT LIVE-SOURCE edits, both on the idiom `pure_ast.py` already uses: PEP-526 local
annotations `guard: Optional["ExprIR"] = None` in `case_block` (and none other landed). No
`typing` import was added anywhere — lesson (ss) holds.

## THE CHEAP ARM TIER IS CLOSED — two refutations measured it

Both spikes reverted cleanly; nothing landed. **Do not re-grind these without the named
capability.**

- **`_sequence_pattern` — blocked, lesson (aq).** Its `name = None if nm.string == "_" else
  nm.string` is an `Optional[str]` local built by a TERNARY, which the campaign's carrier does not
  handle: the union constructor wraps the WHOLE ternary (so the absent name erases to `""` — an
  empty-name facade) and the annotated local is BRANCH-SCOPED (`unbound symbol 'name'`).
  **Reopening capability:** lower an `IfExpr` with a `None` arm per-branch to the union's arm
  constructors, and pre-declare such a local at function top (union locals are currently excluded
  from `pre_decl_vars` by `typed_local_vars`, so they are `let`-bound where first assigned —
  statements.py:4797). Both halves are in `\trusted` mirrors, so the §10.4 price is 0.
  The `MatchSequence`/`MatchStar` arms and the `iropt_str` payload slot were written and work;
  they were reverted with the spike.
- **`async_stmt` — blocked, lesson (ar).** Three passthroughs and an error, every callee already
  interfaced, and still blocked: `self.funcdef([], async_=True, start=t)` passes a real token, and
  the CONCRETE sibling application coerces against `_resolve_dotted_signature`, which does not
  resolve a synthesized `_union_*` (`Optional[τ]`) PARAMETER type — so a coercion arm added to
  `_coerce_dotted_args` never fires. **Reopening capability:** resolve `Optional[τ]` param types in
  `_resolve_dotted_signature`. **The shortcut is refused**: erasing the token actual to `0` because
  the param is int-erased anyway is lesson (al)'s defect (unlike `[]`, a token is a faithful
  value).

## Pick up here — in this order

1. **Build lesson (aq)'s capability** (ternary-`None` union arm selection + function-top pre-decl
   of a union local). Both halves are FREE (`\trusted` mirrors), and it immediately re-lands the
   already-written `MatchSequence`/`MatchStar` arms + `iropt_str` slot + `_sequence_pattern`.
   The `iropt_str` payload arm is also what `try_stmt`'s `ExceptHandler(type, name, body)` and
   `closed_pattern`'s `MatchAs(pattern=None, name=None)` will need, so it is worth more than the
   one conversion.
2. **Then lesson (ar)'s** (`Optional[τ]` param types in `_resolve_dotted_signature`) → `async_stmt`,
   and probably `decorated` (whose `decorators` seq local hits the same coercion path).
3. **The VARIABLE-CLASS-NAME recognizer** is now the biggest single blocker left in this file:
   `cls = "AsyncWith" if async_ else "With"` / `"TryStar" if is_star else "Try"` /
   `"AsyncFunctionDef" if async_ else "FunctionDef"` / `"AsyncFor" if async_ else "For"` gate
   `with_stmt`, `try_stmt`, `funcdef`, `for_stmt`. Note this is the SAME ternary-of-two-literals
   shape as (aq) — build them together if the shapes really coincide. But check the FIELDS first:
   `for_stmt`/`with_stmt` also need `_for_target`/`_with_item`, which are behind the `_set_ctx`
   CORRECTNESS boundary, so the recognizer alone probably only reaches `try_stmt`.
4. **The un-gated `-> "List[ExprIR]"` faithfulness gain** (previous handoff's item 4) is still
   unclaimed: ~75 min of proving to type `expressions`/`statements`/`stmt_control_flow`'s
   `_es`/`_ss` shims as `array emit_ir` instead of `array int`.

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_set_ctx(node, _N("Store")())` — CERTIFIED-BOUNDARY [CORRECTNESS].** `emit_ir` is an
  IMMUTABLE ADT and `ctx` IS a modelled field, so an in-place `ctx` mutation cannot be expressed
  and dropping it would be a LIE. Blocks `namedexpr_test`, `_comp_target`, `_for_target`,
  `expr_stmt`, `del_stmt`, `_with_item`, `atom_paren`'s tuple arm. Reopening capability: a
  functional `set_ctx : emit_ir -> string -> emit_ir` in the LIVE SOURCE.
- **`_subscript_item` — [MODEL].** Needs flow-sensitive narrowing.
- **`_binop` / `global_stmt` — [RECOGNIZER].** `_N(<const-dict read>)()` takes a VARIABLE class
  name. (`for_stmt`/`with_stmt`/`funcdef`/`try_stmt` are the TERNARY sub-case; see item 3 above.)
- **`_pattern_number` — [MODEL].** `Constant(value=_parse_number(tok.string))`: `_parse_number` is
  opaque, so wrapping its result in `PVInt` would claim a float literal is an int. Needs the
  parser's own number classification, or a `pyconst_val` value the opaque call can carry.
- **`atom_list` / `atom_brace` — [MODEL].** `ListComp.generators` is a list of harvested
  `comprehension` RECORDS (a payload slot type the family does not have), and `atom_brace` appends
  `None` KEYS into a list (optional list ELEMENTS).
- `_py_stmts_to_ir`: CERTIFIED-BOUNDARY [COST/SCALE]. `for`-over-array termination: the SOURCE
  cannot supply a variant.

## The §10.4 RE-PORT PRICE LIST (re-measured where touched this window)

| mirror | goals | wall clock |
|---|---|---|
| any `\trusted` mirror body | — | **0** |
| `module6_whyml/types` | 655 | ~8 min |
| `Module6_WhyMLTranspiler` | 706 | ~10 min |
| `frontend/pure_ast` | **1022** (was 808) | ~18 min + a ~10 min vacuity tail |
| `module6_whyml/statements` | 884 | ~15 min |
| `module6_whyml/stmt_control_flow` | 1821 | ~42 min |
| `module6_whyml/functions` | **1175** (was 1167) | ~45 min + vacuity |

**Trusted mirrors you can edit for FREE** (re-verified this window): everything in the previous
list PLUS `expressions._coerce_dotted_args`, `statements._typed_local_vars`,
`statements._handle_expr_stmt`, `statements._emit_body_code`. `frontend/ir_resolve` and
`module6_whyml/preamble`'s `_pyast_*` helpers, and `expressions._call_irnode_constructor`, have no
mirror counterpart at all — also free.
**Un-trusted (costed) ones you WILL hit:** `functions._compute_return_type` /
`_build_method_return_type_map`, `types._field_type_of`, `statements._handle_fieldassign_stmt` /
`_wrap_body_with_return_catch`, `stmt_control_flow._handle_return_stmt`.

## Instrument facts (unchanged, still true, still silently corrupting)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. **The Alt-Ergo pin at `pycsl.py:1318` is stale.** Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
   EXPLICITLY. Do NOT edit the pin.
4. `check-emitted-vacuity.py` is a false green without `--emit`.
5. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files. `--keep-mlw` writes
   `<source>.mlw` NEXT TO THE SOURCE, so remember to delete it.
6. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
7. **A HEAD worktree has no `.venv`**, and `bin/byte-diff-sweep.sh` uses `$ROOT/.venv/bin/python3`:
   without a symlink it emits ZERO files and the diff still reports 0. `ln -sfn <repo>/.venv
   <worktree>/.venv` first.
8. `python3 -u` on every proof, or the log stays empty until the run ends.
9. The Bash tool caps a foreground command at 10 minutes. Run the proof with `nohup ... &` and
   WAIT with an `until ! kill -0 <pid>; do sleep 20; done` loop (a foreground `until`-loop with a
   600 s tool timeout is accepted; a bare `sleep` is blocked).

## THE FASTEST THING THIS WINDOW LEARNED — use it

**An emit-only run is a 30-second oracle.**
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --no-proof
--keep-mlw` type-checks (L3-tc is ON — this is NOT the `--no-typecheck` sweep, lesson (ww) does
not apply) and leaves the `.mlw` for inspection. Every capability in this window was designed by
porting a body, emitting, READING the emitted WhyML for facades, and iterating — before spending a
single minute of proof time. Six emit runs cost less than one proof. Do this first, always.

## Method notes this window paid for (full text in wall-lessons.md, (am)-(ar))

- **(am)** "the annotation has no effect" almost always means you measured the wrong half. PROBE
  the emitter (a 4-line stderr print inside the function) before concluding it is not the decision
  point; and assume TWO producers when a type appears both on a definition and at its call site.
- **(an)** promote a stub's return type to the FILE's convention, not the source language's.
- **(ao)** `[]` lowers to a 1024-long ZERO array that pattern-matches as an array argument.
- **(ap)** a gap-free keyword binding does not have to reach full arity.
- **(aq)** an `Optional[τ]` local built by a TERNARY is a different, unsupported shape.
- **(ar)** a concrete sibling application coerces against `_resolve_dotted_signature`, which does
  not resolve `Optional[τ]` param types — and the erase-the-actual shortcut is refused.
- Still live from before: **(ai)** never stack whole-file proofs (obeyed — every proof this window
  ran sequentially); **(ak)** an assumed clause must be consumed in the same increment (obeyed —
  and the two refutations reverted their clauses with them); **(ac)** read every emitted record
  literal for `Array.make 0 0`.

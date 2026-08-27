# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #6 worker)

## State, verified from the surface

- **Count: MARKERS 549 · grep-substring 574 · offset 25 · unattached 0.** Quote BOTH.
  Get them from **`bin/count-trusted-directives.py`**, never a hand-rolled grep — the grep figure
  counts SUBSTRING hits and 25 of them are one boilerplate module-docstring line repeated across
  25 mirror files. Every DELTA in the record is right; every absolute "the floor is N" from before
  the gate existed (including the famous 687) inherits the +25.
  **Window delta: markers 577 -> 549, grep 602 -> 574 — TWENTY-EIGHT conversions in thirteen
  committed increments.** Best rate of the campaign; the reason is one capability, below.
- Ledger **3**, untouched. No new axiom this window. Every bridge added is a `val` with pointwise
  postconditions (the `materialize`/`snapshot` shape), never an `axiom`.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 compared / 7 known drift / 0 NEW. check-untrusted-emitted **761/744/0/0**.
  emitted-vacuity `--emit`: no NEW erasure, 0 input-blind. Corpus byte-diff **0 over 813/813**.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache`, untracked `scratchpad/`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact.

## THE ONE THING TO UNDERSTAND: the sum type is `emit_ir`, and it already existed

wall-lessons (zz) measured that 34 of the 42 still-`\trusted` `_fin`-gated `_Parser` methods have a
PASSTHROUGH return and concluded "fund `pyast_expr` Stage B" — a NEW recursive ADT, a purity
retrofit of every harvested record, a `pxlist`, a new structural measure. **None of that was
needed** (lesson (ad)). The `-> "ExprIR"` RETURN INTERFACE already gives every un-converted sibling
the type `emit_ir`, so the passthrough half was solved before the wall was written; only the
CONSTRUCTION half was missing. And `emit_ir` is already recursive, pure, certified, and carries
`size`.

The whole capability is **one table**, `frontend/ir_resolve.py::_PYAST_IRNODE_CTORS`, mapping a
pure_ast node class to an `emit_ir` constructor plus its payload in ASDL field order, driving four
consumers that therefore cannot drift:

| consumer | what it does |
|---|---|
| `preamble._pyast_ctor_arms` | the ADT arms |
| `preamble._pyast_kind_of_arms` | the `kind_of` arms (NO `_` catch-all — a missing arm is a 30s Timeout on `kind_of'vc`) |
| `expressions._call_irnode_constructor` | the BY-NAME payload binding; an unbound slot DECLINES |
| `ir_resolve._harvest_pyast_ctor_params` | `init_params`, read STRUCTURALLY off `_NODE_SPEC`, with a fail-closed drift check |

Gated everywhere by `preamble._uses_pyast_parser()` = "this file defines `_Parser._fin`".

**Payload slot types now supported:** `emit_ir` (a child node), `string` (a 0-field ASDL singleton,
carried as its CLASS NAME — lesson (ae); no enum, no axiom), `irlist` (a variadic child list, via
`seq_to_irlist`), `iropt_ir` (a genuinely optional child, via the raw-keyword re-lowering).

**Arms landed:** IrPyAwait, IrPyIfExp, IrPyUnaryOp, IrPyStarred, IrPyName, IrPyAttribute,
IrPyMatchAs, IrPyBoolOp, IrPyMatchOr, IrPyTuple, IrPyYield, IrPyYieldFrom, IrPyBinOp, IrPyIf,
IrPyWhile.

**Adding the next arm is now ~20 minutes plus one 12-minute pure_ast proof.** That is the cheapest
work on the board and it should be the default move.

## THE §10.4 RE-PORT PRICE LIST — measured this window, use it before designing

A change's home is decided by which mirror it perturbs (lesson (vv)). All driver-verified fresh,
sequential, 0 non-Valid, SUCCESS:

| mirror | goals | wall clock |
|---|---|---|
| any `\trusted` mirror body | — | **0** |
| `module6_whyml/types` | 655 | ~8 min |
| `Module6_WhyMLTranspiler` | 706 | ~10 min |
| `frontend/pure_ast` | 808 | ~12 min |
| `module6_whyml/statements` | 884 | ~15 min |
| `module6_whyml/stmt_control_flow` | 1821 | ~42 min |
| `module6_whyml/functions` | 1167 | ~50 min |
| `frontend/Module5_IREmitter` | 1111 | (relaunch #5) |

Goal count is NOT a time predictor. Both big ones spend most of their wall clock in a long
single-goal tail AFTER the last printed result — exactly the shape that looks like a hang.
**Never run two whole-file proofs at once** (lesson (ai)): four in parallel took load to 20 on 12
cores and ALL FOUR stalled for 17 minutes.

**Trusted mirrors you can edit for free** (verified this window): `Module6_WhyMLTranspiler.transpile`,
`expressions._handle_dotted_call`, `expressions._handle_call_expr`, `expressions._resolve_dotted_signature`,
`Module5_IREmitter._py_expr_call`, `Module5_IREmitter.visit_Module`,
`preamble._emit_preamble_exceptions`, `preamble._emit_preamble_uses`,
`statements._collect_array_elem_types` and the SQ1 promotion block.
**Un-trusted (costed) ones you WILL hit:** `functions._compute_return_type` /
`_build_method_return_type_map`, `types._field_type_of`, `statements._handle_fieldassign_stmt` /
`_wrap_body_with_return_catch`, `stmt_control_flow._handle_return_stmt`.

## Pick up here — in this order

1. **KEEP ADDING ARMS. This is the highest-yield, lowest-risk work left.** Each is: one
   `_PYAST_IRNODE_CTORS` entry + the verbatim mirror body port + one pure_ast proof. Immediately
   reachable, in rough order of cheapness:
   - `_pattern_number` (`Constant` + `UnaryOp`; needs a `PyConstVal` slot — the `pyconst_val` ADT
     already exists),
   - `atom_list` (`List` / `ListComp`), `atom_brace` (`Dict`/`Set`/`DictComp`/`SetComp`),
   - `_sequence_pattern` (`MatchSequence` + `MatchStar`, the latter with an `iropt_str` slot),
   - `closed_pattern` (`MatchValue`/`MatchSingleton`/`MatchClass`),
   - `comparison` (`Compare`; needs a STRING-list payload — either a `strlist` cons-list beside
     `irlist`, or accept the op names as an `irlist` of `IrStr`, which is lossless but muddies
     `kind_of`; prefer `strlist`).

2. **`statement` is blocked on ONE named piece**: `self.funcdef([], async_=False)` passes an EMPTY
   LIST LITERAL to a param the model int-erases (`decorators: Any`), and `(Array.make 1024 0)`
   ill-types against the abstract val's `int` param. Fix in `_coerce_dotted_args` (whose caller
   `_handle_dotted_call` is `\trusted`): an empty array literal against an `int` param lowers to
   `0`. Everything else in `statement` already emits correctly. Yield: `statement`, and then
   `parse_module` above it.

3. **`block` / `small_stmt` need the STATEMENT half of the ctor family.** `small_stmt`'s eleven
   passthroughs return `Return`/`Raise`/`Import`/`ImportFrom`/`Assert`, which earlier windows
   converted as PER-CLASS RECORDS. Typing it means migrating those five from records to emit_ir
   arms — which also means `alias` becomes an arm (for `Import.names`) and `_dotted_as_name` /
   `_import_as_name` / `_import_as_names` change shape. All within pure_ast (1 mirror), so the
   price is one 12-minute proof, but it re-shapes eight already-converted bodies: do it as ONE
   batched increment and read every emitted record literal for `Array.make 0 0` (lesson (ac)).

4. **The un-gated `-> "List[ExprIR]"` faithfulness gain.** Increment 11 gated
   `_compute_return_type`'s new branch on `_uses_pyast_parser` purely to keep the sweep at 2 of 52.
   Un-gated it also types `expressions`/`statements`/`stmt_control_flow`'s `_es`/`_ss` shims as
   `array emit_ir` instead of `array int` — a real gain, priced at ~75 min of proving. Worth a
   dedicated increment.

## RECORDED BOUNDARIES — do not re-grind without new capability

- **`_set_ctx(node, _N("Store")())` — CERTIFIED-BOUNDARY [CORRECTNESS].** `emit_ir` is an
  IMMUTABLE ADT and `ctx` IS a modelled field, so an in-place `ctx` mutation cannot be expressed
  and dropping it would be a LIE. Blocks `namedexpr_test`, `_comp_target`, `_for_target`,
  `expr_stmt`, `del_stmt`, `atom_paren`'s tuple arm. Reopening capability: a functional
  `set_ctx : emit_ir -> string -> emit_ir` in the source, i.e. a LIVE refactor — not an emitter fix.
- **`_subscript_item` — [MODEL].** `lower = upper = step = None` then `return lower` returns the
  Optional-union LOCAL in an emit_ir position, so the model must project it with the sentinel
  (None-reads-as-a-node) even though that path is dynamically unreachable. Needs flow-sensitive
  narrowing.
- **`_binop` / `global_stmt` / `for_stmt` / `with_stmt` — [RECOGNIZER].** `_N(<variable>)()` /
  `_N(cls)(...)` take a VARIABLE class name (from `_BINOP`, `_UNARY`, or an `async_` ternary), which
  the class-by-name recognizer cannot resolve. Reopening capability: resolve `_N(<const-dict
  read>)()` / `_N(<ternary of two literals>)()` to the finite set of classes it can name.
- `_py_stmts_to_ir`: CERTIFIED-BOUNDARY [COST/SCALE] (unchanged).
- `for`-over-array termination: the SOURCE cannot supply a variant (unchanged).

## Instrument facts (unchanged, still true, still silently corrupting)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. **The Alt-Ergo pin at `pycsl.py:1318` is stale.** Pass `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'`
   EXPLICITLY. Do NOT edit the pin.
4. `check-emitted-vacuity.py` is a false green without `--emit`.
5. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
6. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
7. **A HEAD worktree has no `.venv`**, and `bin/byte-diff-sweep.sh` uses `$ROOT/.venv/bin/python3`:
   without a symlink it emits ZERO files and the diff still reports 0 (lesson (k), hit again this
   window). `ln -sfn <repo>/.venv <worktree>/.venv` first.
8. `python3 -u` on every proof, or the log stays empty until the run ends.
9. The Bash tool caps a foreground command at 10 minutes. Run the proof with `nohup ... &` and WAIT
   INSIDE YOUR OWN TURN with a `kill -0` poll loop. Never END a turn with one running.

## Method notes this window paid for (full text in wall-lessons.md, (ad)-(aj))

- **(ad)** The sum type already existed. Before funding a new value model, ask whether an EXISTING
  certified one has the shape and whether another lever already solved half the problem.
- **(ae)** A 0-field ASDL singleton is completely modelled by its class-name STRING. Harvest the
  membership from `_NODE_SPEC`, NOT from `_PURE_AST_FIELD_TABLE` (which lists only classes WITH
  fields — the first attempt produced an empty set and the lowering silently did not fire).
- **(af)** A multi-million-step Timeout is almost never "a hard goal". Read the goal NAME:
  `<theory fn>'vc` = you broke an ADT match's exhaustiveness; a cursor postcondition = a callee is
  missing its monotonicity export.
- **(ag)** (ww) again — a four-line innocuous mirror diff was an L3-tc ERROR. The leak was a
  COUPLING; removing it was cheaper AND safer than patching it.
- **(ah)** A local first assigned inside a conditional BRANCH is scoped to that branch; a list field
  bound from it silently becomes `Array.make 0 0`.
- **(ai)** Never stack whole-file mirror proofs.
- **(aj)** Re-cost a §10.4 re-port refused once, when the same blocker reappears with a bigger yield.
- **NEW, uncodified but important:** an ASSUMED clause on a `\trusted` stub (`-> "ExprIR"`,
  `ensures self.i >= \old(self.i)`) is a TCB ADDITION. It must unlock a conversion in the SAME
  increment. This window reverted fourteen such clauses that unlocked nothing.

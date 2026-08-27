# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #5 worker)

## State, verified from the surface

- **Count: MARKERS 578 · grep-substring 603 · offset 25 · unattached 0 · stale 0.** Quote BOTH.
  Get them from **`bin/count-trusted-directives.py`**, never a hand-rolled grep — the grep figure
  counts SUBSTRING hits and 25 of them are one boilerplate module-docstring line repeated across
  25 mirror files. Every DELTA in the record is right; every absolute "the floor is N" from before
  the gate existed (including the famous 687) inherits the +25.
  **Window delta: markers 586 -> 578, grep 611 -> 603 — EIGHT conversions in six committed
  increments.**
- Ledger **3**, untouched. No new axiom, no new certificate needed this window.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache`, untracked `scratchpad/`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact — do NOT delete or re-arm it.
- Fidelity at the standing baseline **2 DIVERGED / 3 drifted** (`_handle_var_expr`,
  `_handle_for_stmt`; the three "mirror def not in source" are cross-file bridge stubs).
  Field parity 335 compared / 7 known drift / 0 NEW. check-untrusted-emitted **732/715/0/0**.
- Proofs standing at HEAD: `frontend/pure_ast` **401 Valid** (299 at window start),
  `module6_whyml/stmt_control_flow` **1797 Valid**, `frontend/Module5_IREmitter` **1111 Valid** —
  all 0 Unknown/Timeout/Invalid, all SUCCESS; pure_ast's runs include the built-in vacuity phase.
  Corpus byte-diff **0 over 813/813**.

## Instrument facts (unchanged, still true, still silently corrupting)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. **The Alt-Ergo pin at `pycsl.py:1318` is stale.** Pass
   `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY. Do NOT edit the pin.
4. `check-emitted-vacuity.py` is a false green without `--emit`.
5. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
6. **`bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — when run with no
   PATH export.** Export PATH; optionally pass a path prefix to scope it.
7. **The Bash tool caps a foreground command at 10 minutes.** A whole-file mirror proof exceeds
   that. Run it with `run_in_background` writing to a log, then WAIT INSIDE YOUR OWN TURN with a
   `Monitor` until-loop. That is still foreground work in the sense the process rules mean — what
   is forbidden is ENDING A TURN with an ownerless writer running.
8. `python3 -u` on the proof, or the log stays empty until the run ends and you cannot see
   progress at all.

## What this window did

**THE LADDER'S ITEMS 1 AND 2 ARE DONE, and both of item 2's recorded blockers were REFUTED.**

- `accept_kw`/`at_kw` monotonicity chain — the five-minute repeat of `accept_op`'s, as predicted.
- **`expect_op` / `expect_kw` take an UNCONDITIONAL `ensures self.i > \old(self.i)`** — STRONGER
  than `accept_*`'s conditional clause, because their reject path is the `-> "NoReturn"` `error`.
  Zero TCB, count-neutral, and it is what makes a `while self.at_kw(...)` loop measurable.
- **`_import_as_names` CONVERTED (586 -> 585).** "`List[<harvested record>]` is a monomorphizer
  gap" is FALSE: Module5 never PARSES a quoted parametric return annotation at all (lesson (tt)).
  And a METHOD's function-IR name is MANGLED, so the ir_resolve pass that should have patched it
  was silently no-opping (lesson (uu)).
- **`parse_eval` CONVERTED (585 -> 584)** via `Expression` in `_PURE_AST_FIELD_TABLE` plus the
  **RETURN INTERFACE lever**: a stub that STAYS `\trusted` can still be given a faithful return
  type (`testlist -> "ExprIR"`), which unlocks its callers at ZERO marker cost. This is the
  cheapest move in the whole vein — do it before attempting any caller.
- **A THIRD seq->array return bridge** (`materialize_<rec>`, beside `materialize` for `seq int`
  and `materialize_str` for `seq string`), declared from `functions.py::_emit_function` and
  triggered by the EMITTED BODY naming it.

**Proofs standing at HEAD**: `frontend/pure_ast` **316 Valid** (was 299), `module6_whyml/
stmt_control_flow` **1797 Valid** (base at HEAD measured 1692), both 0 Unknown/Timeout/Invalid,
both SUCCESS. Corpus byte-diff **0 over 813/813**. Mirror emission diff **2 of 52**.

## What this window did (six committed increments, all fully gated)

1. `at_kw`/`accept_kw` monotonicity chain, and `expect_op`/`expect_kw` UNCONDITIONAL strict
   progress (their reject path is the `-> "NoReturn"` `error`). Count-neutral, zero TCB.
2. **`_import_as_names`** — both recorded blockers refuted (lessons (tt)/(uu)); a THIRD
   seq->array return bridge `materialize_<rec>`.
3. **`parse_eval`** — `Expression` in `_PURE_AST_FIELD_TABLE` + the RETURN INTERFACE lever.
4. **`comp_for`** — a `List[comprehension]` return with a nested cursor-measure loop; purity is
   TRANSITIVE THROUGH A LIST FIELD; a ghost cursor snapshot (lesson (xx)).
5. **`_lambda_arg`** — the `_fin` position-wrapper recognizer, and a literal `None` keyword bound
   to an `option` field now lowers to `None` instead of the int `0`.
6. **`return_stmt` + `assert_stmt` + `_param_arg`** — the `Optional[ExprIR]` LOCAL carrier
   (lesson (ab): the `Optional[X]` collapse is right for a param/field and wrong for a local, and
   the seams are disjoint).
7. **`raise_stmt`** — and its `Raise` table entry also retypes `_py_stmt_raise`'s param in the
   Module5 mirror from an opaque int to the real record.

## Pick up here — in this order

1. **THE REACHABLE `_fin` SET IS NOW 9, and they are itemised.** Of the original 57 `_fin`-gated
   stubs only 13 ever had a single-class return (lesson (zz) — 40 have a PASSTHROUGH return and
   are unreachable with per-class records); 4 of the 13 are converted. The remaining nine:
   `type_alias_stmt`, `del_stmt`, `import_stmt`, `import_from`, `if_stmt`, `while_stmt`,
   `match_stmt`, `lambdef`, `_dict_rest`. Their named gates:
   - `import_stmt` / `import_from` need a **`List[<harvested record>]` FIELD tag** (a list of
     `alias`). `_PURE_AST_FIELD_TABLE` has `ExprIRList` / `StmtIRList` but no record-list tag; the
     downstream machinery already exists (`_bind_listfield_from_seq` + the preamble's
     `value_type in self._record_types` branch). CHEAPEST remaining item.
   - `del_stmt` needs the **0-field ASDL singletons** (`_N("Del")()`); so do `_for_target`,
     `_with_item`, `_subscript`, `_comp_target`, `trailers`, `power`. See item 3.
   - `if_stmt` / `while_stmt` / `match_stmt` need statement-list fields plus `block` /
     `_else_block` / `_if_tail` return interfaces.
   - `_binop` is NOT reachable at all: `_N(opname)()` takes a VARIABLE class name.

2. **THE REAL MASS IS THE SUM TYPE.** 40 of the 57 `_fin` stubs, and most of the 86 non-`_N`
   stubs, need the pure_ast node classes to be ARMS OF ONE TYPE rather than per-class records —
   `return x` beside `return self._fin(_N("BinOp")(...), t)` cannot type otherwise. This is the
   same capability the `pyast_expr` Stage-B item asks for. **Fund that before widening the field
   table further.**

3. **0-field ASDL singletons need a base-category ENUM VARIANT.** A 0-field WhyML record is not
   expressible. `_NODE_SPEC` gives each singleton's category (`expr_context`, `operator`,
   `boolop`, `unaryop`, `cmpop`), so the whole membership is statically known and the ADT is
   axiom-free. COST/SCALE: the `ctx`/`op` field tags move from `"int"` to the category type.

4. Stage B of the `pyast_expr` build — retires the four abstract vals the relaunch-#4 dispatch
   conversions introduced, and is the same capability item 2 needs.

5. `_py_stmts_to_ir`'s six named features (two extend the CERTIFIED `stmt_ir` ADT, so the
   certificate must be extended under the co-landing rule).

## RECORDED BOUNDARIES — do not re-grind without new capability

- `_py_stmts_to_ir`: CERTIFIED-BOUNDARY [COST/SCALE], refuted by a measured erasure probe.
- `for`-over-array termination: the SOURCE cannot supply a variant (the counter is
  emitter-internal). Capability gap, not an annotation gap.

## Method notes this window paid for (full text in wall-lessons.md, (tt)-(ww))

- **(tt)** A QUOTED parametric annotation and its bare twin take DIFFERENT emitter branches. Before
  calling something a capability gap, establish which AST node the emitter actually sees.
- **(uu)** A method's function-IR name is mangled; a bare-name lookup into `ir_data["functions"]`
  is a silent no-op for every method. Print the keys before theorising.
- **(vv)** Where a live-emitter change GOES is decided by the §10.4 re-port cost. A helper-method
  refactor here would have forced two mirror re-proofs AND a new `\trusted` stub — i.e. it would
  have ADDED a marker to save one. Prefer primitives the mirror already models.
- **(ww)** **The mirror emission sweep runs `--no-typecheck`.** A re-ported body can be ill-typed
  and the sweep still reports a clean diff. Run `--no-proof --typecheck` on every changed mirror
  BEFORE queueing its proof. (I lost a proof run to this.) And an abstract sibling val's parameter
  types are inferred from the argument shapes already seen at its call sites — a differently-typed
  new argument is a type error there.
- **DO NOT add a `typing` import to `pure_ast`** (lesson (ss), still true): `List`/`Set`/`Dict`/
  `Tuple` are ASDL node names in that module's own globals. Use the quoted form.

# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #5 worker)

## State, verified from the surface

- **Count: MARKERS 584 · grep-substring 609 · offset 25 · unattached 0.** Quote BOTH. Get them
  from **`bin/count-trusted-directives.py`**, never a hand-rolled grep — the grep figure counts
  SUBSTRING hits and 25 of them are one boilerplate module-docstring line repeated across 25
  mirror files. Every DELTA in the record is right; every absolute "the floor is N" from before
  the gate existed (including the famous 687) inherits the +25. Window delta: markers
  **586 -> 584**, grep **611 -> 609**.
- Ledger **3**, untouched. No new axiom, no new certificate needed this window.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache`, untracked `scratchpad/`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact — do NOT delete or re-arm it.
- Fidelity at the standing baseline **2 DIVERGED / 3 drifted**
  (`_handle_var_expr`, `_handle_for_stmt`; the three "mirror def not in source" are the
  cross-file bridge stubs). Field parity 335 compared / 7 known drift / 0 NEW.

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

## Pick up here — in this order

1. **INCREMENT 3 IS BUILT, L3-tc GREEN, AND NOT YET LANDED.** `comp_for` (a
   `List[comprehension]` return with a nested cursor-measure loop). The apply script is
   `getting-better/pure-ast-inc3/apply_inc3.py` (pure_ast + `_PURE_AST_FIELD_TABLE`) and the
   three emitter hunks are `getting-better/pure-ast-inc3/{expressions,preamble,statements}.py.diff`
   (apply with `git apply -p1` from the repo root; verified to apply cleanly). It needed TWO new emitter
   capabilities, both in functions whose mirrors are ALREADY `\trusted`, so §10.4 costs NOTHING:
   - a seq local appended from a CALL whose declared return is an IR-node tag now records its
     `emit_ir` element type. Without it `_bind_listfield_from_seq` refuses and the record's list
     field falls back to `Array.make 0 0` — **a DROPPED-CHILD FACADE that type-checks**;
   - **purity is TRANSITIVE THROUGH A LIST FIELD.** A pinned `List[<record>]`-element record with
     an `array emit_ir` field is still Why3-rejected ("instantiates pure type variable 'a with a
     mutable type"), so for a pinned record the list field is emitted as the pure `seq <elem>` —
     which is exactly the shape the filling local already has, so no `Init.init` at all.
   Outstanding for it: corpus byte-diff, mirror sweep, whole-file proof.

2. **THE `_fin` CAPABILITY — 57 stubs, ~10% of the whole TCB, and it is a CALL-SITE RECOGNIZER,
   not a monomorphization.** `_fin`/`_fin_block`/`_fin_pos`/`node` set only the four ASDL
   location attributes and return the node unchanged. **The harvested `_NODE_SPEC` records do not
   carry those attributes at all**, so in the model `_fin(x, t) == x`, and lowering the call to
   its first argument is faithful. Gate it on the constructed node's record having no
   `lineno`/`col_offset`/`end_lineno`/`end_col_offset` field so it fails CLOSED if the harvest is
   ever widened. It goes beside the `_N` recognizer in `Module5_IREmitter._py_expr_call`, **whose
   mirror is `\trusted`** — so no §10.4 port, no mirror re-proof. Full argument in the backlog
   section "pure_ast VEIN, RELAUNCH #5".

3. **Widen `_PURE_AST_FIELD_TABLE` on demand** — 22 of 76 `_NODE_SPEC` entries are in it. The 13
   non-`_fin` `_N`-constructing stubs and the classes they need are tabulated in the backlog.
   `_binop` is NOT reachable this way: `_N(opname)()` takes a VARIABLE class name.

4. **0-field ASDL singletons (`Load`/`Store`/`Pow`/…) need a base-category ENUM VARIANT** — a
   0-field WhyML record is not expressible. `_NODE_SPEC` gives each one's category, so the whole
   membership is statically known and the ADT is axiom-free. COST/SCALE (the `ctx`/`op` field
   tags move from `"int"` to the category type).

5. Stage B of the `pyast_expr` build (recursive ADT, structural variant) — retires the four
   abstract vals the relaunch-#4 dispatch conversions introduced.

6. `_py_stmts_to_ir`'s six named features (two extend the CERTIFIED `stmt_ir` ADT, so the
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

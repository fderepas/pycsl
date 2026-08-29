# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-29, RELAUNCH #14 worker)

## State, verified from the surface at end of session

- **Count: MARKERS 503 · grep-substring 528 · offset 25 · unattached 0.** Quote BOTH.
  From **`bin/count-trusted-directives.py`**, never a hand-rolled grep — 25 of the grep
  hits are one boilerplate module-docstring line repeated across 25 mirror files, so every
  historical absolute figure (the famous "687") is overstated by that 25.
  **Window #2 delta so far: markers 530 -> 503, grep 555 -> 528.**
  **This session (#14): 508 -> 503 — FIVE conversions in five gated increments, TWO
  recorded CERTIFIED-BOUNDARIES broken, TWO live emitter facades found and fixed.**
- **`bin/check-shadowed-selfcalls.py`: 27 CONVERTED methods / 176 bypassing call sites,
  ratchet 27** — unchanged. Needs `TMPDIR=/home/fabrice/git/pycsl/scratchpad`.
- Ledger **3**, untouched. Emitted axioms in pure_ast: **0**. Literal-guard grep: **0**.
- **PROOF COSTS, MEASURED THIS SESSION (the campaign had none of these numbers):**
  `frontend/pure_ast` **2792/2792**, ~25 min proving + ~35 min non-vacuity.
  `module6_whyml/statements.py` **904/904**, ~23 min total.
  `frontend/Module5_IREmitter.py` **1115/1115**, ~30 min proving + ~20 min non-vacuity.
  A single corpus driver (`0447`) is **11 seconds**.
- Fidelity at the standing baseline **2 DIVERGED** (`_handle_var_expr`, `_handle_for_stmt`).
  Field parity 335 / 7 known drift / 0 NEW. check-untrusted-emitted **807 / 790 / 0 / 0**.
  emitted-vacuity `--emit`: no NEW erasure, **8 known**. Corpus byte-diff **0 over 813/813**.
  `frontend/pure_ast` proves **2792 / 2792**. `bin/self-annotate-mirror-check.sh` output
  byte-identical to the session-start HEAD baseline.
- Tree clean apart from the pre-existing user/build dirt (`session.txt`, untracked
  `scratchpad/`, `prompt`, `prompt.txt`). Leave it alone.
  `getting-better/.driver-deadline` intact (Sep 1 08:24 UTC). Commits unpushed by design.

## WHAT THIS SESSION LANDED (all five in `frontend/pure_ast`)

1. **`namedexpr_test` (508 -> 507)** — the ladder's cheapest item, taken exactly as the
   previous handoff had analysed it: the live `first = _set_ctx(first, _N("Store")())`
   one-liner, a NEW `IrPyNamedExpr emit_ir emit_ir` ctor (the pre-existing
   `IrNamedExpr string emit_ir` types the target as a STRING and cannot be reused), and the
   re-depthing `namedexpr_test`=13 with `test_or_star` 0->14 and `_call_args` 13->14.
2. **`del_stmt` (507 -> 506)** — the FIRST `_set_ctx` site that was a LOOP VARIABLE.
   Rebinding a loop variable does not propagate into the list, so the SHAPE changed too:
   an INDEXED walk accumulating into a fresh list, runtime-identical, byte-diff 0/813.
   New ctor `IrPyDelete irlist`.
3. **`expr_stmt` (506 -> 505)** — the SIXTH and last `_set_ctx`-blocked stub, closing that
   whole recorded [CORRECTNESS] boundary. Four new ctors (`IrPyExpr`, `IrPyAssign`,
   `IrPyAugAssign`, `IrPyAnnAssign`); two gaps closed by RUNTIME-IDENTICAL SOURCE MOVES
   (bind the token text and read `_AUG` INSIDE the construction — `factor`'s certified
   `_N(_UNARY[t.string])()` shape; pass `type_comment=None` EXPLICITLY so the omitted
   `iropt_str` slot is a TRUE `IrSNone` instead of declining the whole construction to an
   input-blind `assign_0 ()`); ONE new emitter capability —
   `isinstance(x, _N("<Cls>"))` -> `(str_eq_op (kind_of x) "<Cls>")` instead of the
   input-blind `isinstance_op 0 0`.
4. **`small_stmt` (505 -> 504)** — the CERTIFIED-BOUNDARY [HETEROGENEOUS CONVERTED RETURNS]
   BROKEN. Five statement builders migrated off harvested per-class RECORDS onto ctor arms
   (`IrPyReturn`/`IrPyRaise`/`IrPyAssert`/`IrPyImport`/`IrPyImportFrom` + `IrPyAlias`);
   ALL FIVE `py_*` record types are now GONE from the emitted theory. Plus the cost the
   refutation had NOT named: `#@ ensures self.i > \old(self.i)` was a TRUSTED claim, and
   converting made it a proof obligation over thirteen arms whose fall-through is the
   UNGUARDED `return self.expr_stmt()` — 22 contracts gained the strict clause and 7 gained
   a token-kind precondition.
5. **`_fstring_prefix_raw` (504 -> 503)** — `ch.isalpha()` lowered to `ch_isalpha_0 ()`,
   an ARGUMENT-LESS opaque constant on a loop-local. Now `(py_isalpha_op !ch)`.
6. **The `is*` receiver repair UN-GATED (count-neutral, increment 6)** — the one
   deliberately NON-INERT change of this campaign, taken with its price paid.
   `module6_whyml/statements.py` re-proved **904/904 SUCCESS** (identical to the baseline
   measured UNCHANGED first) and corpus driver **0447 re-proved SUCCESS in 11 s**. Corpus
   byte-diff is **1 of 813 BY DESIGN** and that one file is the one re-proved. 0447 is the
   reference driver FOR THIS FEATURE and its contract is about 0/1-ness, which the
   receiver-carrying op still gives.

## THE TWO LIVE EMITTER FACADES FOUND THIS SESSION (both fixed, both are method lessons)

- **A field-NAME set does not determine a payload** (lesson (br)). Adding `Import` — whose
  single ASDL field is also called `names` — put a candidate into `global_stmt`'s
  class-name chain whose `irlist` slot cannot take a `seq string`, and the all-or-nothing
  candidate rule then declined the WHOLE construction: `global_stmt` silently fell back to
  the scalar `0` after six windows of being faithful. **A pure ADDITION to a shared table
  is cross-cutting.** Fixed by narrowing the derivation with the slot TYPES, and by
  SNAPSHOTTING the abstract-val registry across the trial lowering (a declining candidate
  still registered a dangling `val py_import_0 () : int`).
- **A receiver baked into an op NAME is a constant.** `ch.isalpha()` -> `ch_isalpha_0 ()`
  severs the result from the value tested — exactly what the COMPUTED-receiver branch of
  the same dispatcher already refuses in a comment. The dotted branch had never been held
  to its own rule.

## FLAGGED FOR A DEDICATED INCREMENT (measured, not taken)

- (The `is*` receiver repair that was flagged here mid-session was TAKEN as increment 6.
  Corpus byte-diff is now 1 of 813 against the session-start baseline BY DESIGN — the one
  differing file, `0447`, is re-proved. Re-baseline your corpus sweep against the CURRENT
  HEAD, not against a pre-session snapshot.)
- **The Alt-Ergo pin at `pycsl.py:1318` is stale** (2.6.2 vs installed 2.6.3). Keep passing
  `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY; do NOT edit the pin.
- **`_py_stmt_assign` reads `stmt.targets[0]` only** — chained-assignment targets silently
  dropped; the repair is corpus-byte-inert and was reverted (lesson (bk) §2).
- Dropping the `_record_array_fields` PROXY disjunct changes 6 of 813 corpus files
  (lesson (bc)).

## Pick up here — in this order

1. **`Module5_IREmitter._py_stmt_raise` — CERTIFIED-BOUNDARY [OPTIONAL NODE FIELD NOT
   UNWRAPPED], and it is the item with the ONE capability that subsumes most of itself.**
   PROBED this session (spike built on the 1-second oracle, measured, fully reverted). The
   emitted body names every gap at once:
   - `ir_stmts := Seq.snoc !ir_stmts (SUnmodelledStmt_Raise)` — no `SRaise iropt_str
     iropt_ir` arm on the `stmt_ir` ADT (`preamble.py`, FLAT so `size_stmt`'s catch-all
     covers it) and no `_STMT_IR_CTORS` entry. Mechanical.
   - `(if (isinstance_op 0 0) && (isinstance_op 0 0) …)` — `isinstance(stmt.exc, ast.Call)`
     and `isinstance(stmt.exc.func, ast.Name)` are BOTH input-blind.
   - `get_id (get_func stmt.py_raise_exc)` / `get_args stmt.py_raise_exc` — the projections
     are applied to the OPTION rather than through it, which is also the L3-tc error that
     stops the run.
   - two option-carrying child kinds missing from `_lower_stmt_ir_node`: an `Optional[str]`
     LOCAL into an `iropt_str` slot and an `Optional[ExprIR]` LOCAL into an `iropt_ir` slot
     (the existing `opt` kind recognizes only the `disp(x) if x else None` TERNARY).
   **THE ONE CAPABILITY: an OPTIONAL emit_ir RECORD FIELD, guarded non-None by the
   enclosing `is not None`, must PROJECT THROUGH the option** — gaps 2, 3 and 5 are all
   that same missing unwrap. `stmt.exc` is `option emit_ir`, so `_is_emit_ir_expr` says
   False and the whole attribute chain falls to the opaque `get_<attr>` fallback at
   `expressions.py:~11495`. The method-sentinel scoping pattern
   (`_current_emitting_func == "_py_stmt_raise"`, as `_EMIT_IR_HANDLER_ATTR_PROJ` already
   does) keeps it byte-inert everywhere else, and the `None` arm is unreachable under the
   guard so the standard `IrOther ""` filler is honest. The live restructure it also needs
   (compute-then-append instead of mutate-a-dict-then-append) was built and verified
   runtime-identical — same keys, same order — and reverted with the spike.
   Baseline for the gate: Module5_IREmitter proves **1115/1115** at HEAD in ~50 min.
   **THE TWO TRAPS ALREADY MAPPED, so you do not have to find them:**
   - `_is_emit_ir_expr`'s Attribute branch accepts a record field only when its
     `field_types` tag is in `("ExprIR","StmtIR","IRNode","ContractExprIR","emit_ir")`.
     `_PURE_AST_FIELD_TABLE["Raise"]` tags both fields `"OptExprIR"`, which is why the whole
     chain falls to the opaque `get_<attr>` fallback at `expressions.py:~11495`.
   - **Do NOT make the unwrap the general lowering of an `OptExprIR` field read.** The
     `is None` path at `expressions.py:~4488` calls `_optexprir_field_read` and then
     `_expr_to_whyml` on the SAME field to build
     `(match <raw field> with None -> true | Some _ -> false end)`; if the field read
     already unwraps, that guard becomes a match on a match. Either fire the unwrap only
     where the result feeds a further projection / an isinstance subject, or take the
     cheaper route: bind `exc = stmt.exc` in the LIVE body first (runtime-identical) and
     make the LOCAL the unwrap carrier, reusing the `_optional_union_locals` /
     `_union_read_iropt_ir_projection` machinery pure_ast already has.
2. **The two Module5 dispatchers — 142 of the 176 shadowed sites** (`_csl_to_ir` 92,
   `_py_expr_to_ir` 44, `_py_op_to_str` 6). NOTE: these are already CONVERTED (they are not
   `\trusted`), so this is a SHADOWED-metric item, not a marker item. The recorded L2
   TYPE-UNIFICATION wall. "`comprehension` joins the family" is the named shape.
3. **`module6_whyml/struct_format.py` `arity` + `slot_id`** — PROBED this session. The
   mirror models the dataclass field `slots` as a bare `int`; with `slots: List[str]` the
   emitted record field is `array int` (elements int, NOT string) and the file's preamble
   does not `use array.Array` at all, so even the one-line `arity` is an L3-tc error
   (`unbound type symbol 'array'`). Reopening capability, named: a STRING-ELEMENT list
   field on a mirrored dataclass + the preamble scan noticing an array-typed record field.
   `parse_format`/`calcsize` in the same file stay on the regex categorical boundary.
5. **`strings`** — CERTIFIED-BOUNDARY [HETEROGENEOUS TUPLE ELEMENT TYPE], five capabilities
   for one marker. NOTE it now carries a SECOND trusted clause (`ensures self.i >
   \old(self.i)`, added and consumed with `small_stmt`), so converting it also discharges
   that.

## RECORDED BOUNDARIES — do not re-grind without the named capability

- **`strings` — [HETEROGENEOUS TUPLE ELEMENT TYPE]**. `parts` is a seq of 4-TUPLES that
  collapses to a HASH CONSTANT; its three consumers each need their own capability. The
  `kinds` SET is NOT a gap (it models as `map string (option int)`).
- **`_fin`, `_max_end`, `_fin_block` — [ERASURE-LEDGER]** (lesson (bd)). Reopening: an
  `emit_ir` that CARRIES the four ASDL location attrs.
- **`node(self, name, start_tok, **kw)` — [MODEL]**, a `**kw` SPLAT with a run-time class
  name. It now has a RETURN INTERFACE plus real parameter types (`name: str,
  start_tok: _Tok -> "ExprIR"`), which de-hashed the class-name argument; the splat itself
  is still the wall.
- **`_slice`** — needs `self._lines`, a `List[str]` field the mirror's `__init__` does not
  model.
- **`_py_stmts_to_ir` / `_csl_to_ir` / `_py_expr_to_ir` — [L2 TYPE UNIFICATION].**
- **`for`-over-array termination** — the SOURCE cannot supply a variant.
- The **`_Unparser` family (~50 stubs)** — `self.interleave(lambda: …)` and
  `with self.delimit(…)`. A fundamental modelling boundary.
- **`Module2_Parser`'s contract-expression cluster** — recorded TERMINUS; reopen only with
  a per-file raised SMT budget or a body-out-of-context modular mechanism.
- `_decode_escapes` / `_decode_string` — `str|bytes` return, `chr(int(d, 8))`,
  `_unicodedata.lookup`. `_decode_fstring_middle` is one line but is blocked on
  `_decode_escapes` having no honest single return type; splitting it out is NET ZERO
  (one marker converted, one new stub created) unless the split half also converts.
- **`error` / `unsupported`** stay `\trusted` by design; count-neutral.

## Instrument facts (re-verified this session)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path.
3. `check-emitted-vacuity.py` is a false green without `--emit`.
4. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files.
5. `bin/check-untrusted-emitted.py` reports 0/0/0/0 — a FALSE GREEN — with no PATH export.
6. `python3 -u` on every proof, or the log stays empty until the run ends.
7. **A `pycsl.py` run has TWO phases and the second dominates.** `pure_ast` is now ~25 min
   of proving and ~35 min of non-vacuity. **A FAILING run is much FASTER than a passing
   one.** A failure in the PROVING phase shows up in ~20 min; a pass takes ~60.
8. **BACKGROUND WATCHERS DO NOT SURVIVE YOUR TURN ENDING.** `nohup` the proof, then wait in
   the FOREGROUND with `timeout 570 bash -c 'until grep -q ALLDONE …; do sleep 20; done'`
   AND pass the Bash tool's own `timeout` parameter (default 120s will background you).
9. **`scratchpad/w2/sweep.sh <repo-root> <outdir>`** emits all 52 mirrors WITH L3-tc and
   writes `manifest.md5` in ~35 s. `bin/byte-diff-sweep.sh <out>` does the 813 corpus files
   in ~32 s. Keep a HEAD worktree at `…/8f7f6044-…/scratchpad/head-wt`; refresh with
   `git fetch /home/fabrice/git/pycsl <branch> && git checkout -q FETCH_HEAD`.
   **USE IT AS A SPIKE SANDBOX**: build the whole spike there on the 1-second oracle,
   `git diff > patch`, then `git apply` in the main tree. That is how `expr_stmt` and
   `small_stmt` were priced before a single proof minute was spent. Careful: a `cd` into
   the worktree persists for the whole compound Bash command.
10. **`--fun` CANNOT probe this file at all** — the filtered emission puts a `variant`
    clause on a plain `let` ("unexpected 'variant' clause"). Whole-file or nothing.
11. **`bin/check-shadowed-selfcalls.py` has its BASELINE as a constant in the file** and
    takes ~2 min; give the Bash tool an explicit timeout.

## Method notes this session paid for (full text in wall-lessons.md, (br)-(bs))

- **(br)** a field-name set does not determine a payload; a pure ADDITION to a shared table
  is cross-cutting; an all-or-nothing candidate rule turns that into a silent facade; and a
  DECLINED trial lowering leaves fingerprints (snapshot the abstract-op registry).
- **(bs)** a trusted `ensures` is a load-bearing beam and converting is what makes you pay
  for it; strictness is a whole-chain property with `atom` as the base case; a loop with no
  direction invariant DESTROYS a strict step that preceded it; when one postcondition is one
  giant hop, stage it with `#@ assert` (prove-and-assume); sometimes the timeout is a MISSING
  clause (`ensures True` is permission, not neutrality); and **state LESS when the support is
  not there** — `k <= n` where `n = len(raw) - 1` burned 17.2M steps to a Timeout for a fact
  the preceding loop never carried.
- Still live: **(am)** ASSUME TWO PRODUCERS; **(ai)** never stack whole-file proofs;
  **(bl)** grep the emitted body for `if true then` / `&& false` after ANY slot-type change;
  **(bo)** derive the whole depth assignment BEFORE proving; **(bp)** instrument the decision
  when a source bisection convicts an innocent; **(bq)** a returnless mutator is modelled as
  a NO-OP, and the fix is a RETURN INTERFACE.

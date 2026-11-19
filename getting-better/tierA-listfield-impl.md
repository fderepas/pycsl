# `tierA-listfield-impl.md` — impl plan (L9): bind list-valued fields in record construction

Gate P: spike-first, refutation exit, three-L-plane battery, honest scope. All four below.

## The restriction being lifted
`src/pycsl/module6_whyml/expressions.py::_call_record_constructor` (~line 8487):
```python
# Only scalar (int-modelled) fields take a substituted value; a
# list/dict/set field keeps its typed default (array/map construction
# over a param is out of Tier-A scope).
if field_types.get(fn, "int") in ("list", "array", "dict", "set", "frozenset"):
    continue
```
Consequence: `Ctor(a, b, my_list)` emits `{ f_a = ...; f_b = ...; f_list = (Array.make 0 0) }` —
the caller's list is SILENTLY DROPPED. Besides blocking conversions this is a FACADE HAZARD: a stub
that type-checked around it would return a record with an empty list.

## SPIKE TARGET — `Module2_Parser::_ContractParser._parse_for_block` (22 live LOC)
Chosen because it is the only measured target whose OTHER blockers are already cleared:
- Its return route already works (no `-> "ExprIR"` annotation; the emitter emits the `forexpand`
  record literal directly and infers the return type correctly — unlike `_parse_act_block`, whose
  return type came out as `int`).
- Its clause list is already homogeneous (`IrRequires`/`IrEnsures` are both variants; it does NOT
  need the `IrGiven` work).
- The required `ForExpand` field retype is ALREADY VERIFIED to work (below).

**Do NOT spike on** `_parse_act_block` (also needs `IrGiven` + an `Act` return-type route) or on the
`Module1_Ingestor` `_Harvester` trio (`_emit_block_footer`/`run`/`_emit_target` — those append to
`self._out`, so they ALSO need `@mutable_state` on `_Harvester` and a corrected `assigns self._out`
frame; their current `assigns \nothing` is a FALSE FRAME, wall-lesson (f)).

## STEP 0 — the two-part make-or-break spike

**(0a) Field retype — already measured as working, re-apply it.** In BOTH
`src/pycsl/frontend/Module2_Parser.py` and `src/self-annotate/src/frontend/Module2_Parser.py`,
retype `ForExpand`:
```python
    var: str
    lo: "ExprIR"
    hi: "ExprIR"
    clauses: List["ExprIR"]
```
(was `lo/hi: CSLNode`, `clauses: List[CSLNode]`). This is the banked, precedented `CSLNode -> "ExprIR"`
device — 93 scalar `: "ExprIR"` and `List["ExprIR"]` on `CSLCall.args`/`elts` are already in-tree
(precedent commit `ef94162f`). Type hints are runtime-inert. VERIFIED this window: it correctly moves
the field from `array int` to `array emit_ir`.

**(0b) Lift the restriction, minimally and GATED.** Teach `_call_record_constructor` to bind a
list-valued field when the supplied argument is a list-typed local/expression, including the
`seq` -> `array` reconciliation (locals accumulate as `Seq.snoc`; list fields lower to `array`).
Keep the empty-literal case on the existing default path (`NoExceptionDecl(exceptions=[])` is
correctly served by `Array.make 0 0` today — do not regress it).
**Gate the new behaviour as narrowly as you can** so unrelated corpus record constructions keep
emitting byte-identically. Byte-inertness is the acceptance criterion, so prefer the narrowest gate
that makes the spike pass.

Then, with `_parse_for_block` STILL `\trusted`:
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/Module2_Parser.py \
    --import-path src/pycsl --no-proof --keep-mlw
```
**SPIKE PASSES** iff L3-tc is ✓ AND a `grep` of the emitted `.mlw` shows NO
`forexpand_clauses = (Array.make 0 0)` fabrication for a call that supplied a real list.

**REFUTATION EXIT.** If lifting the restriction cannot be made to type-check, or cannot be gated
without changing unrelated emissions, STOP. Revert every file by exact path and report the exact
error. CERTIFIED-BOUNDARY is a fully successful outcome. Do NOT start a general array/seq
theory rewrite — that is the over-build this exit exists to prevent.

## STEP 1 — convert (only if STEP 0 passed)
Port the live `_parse_for_block` body VERBATIM into the mirror, drop `#@ \trusted`, keep
`#@ requires True / ensures True / assigns self.i`, and add the established loop idiom verbatim from
`_parse_qualname` in the same file, immediately above the `while`:
```
#@ loop invariant self.i >= \old(self.i)
#@ loop invariant 0 <= self.i and self.i < \length(self.toks)
#@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
#@ loop variant \length(self.toks) - self.i
```

## STEP 2 — three-L-plane battery (ALL required; `--fun` is NOT a substitute)
**Always pass explicit provers — the repo default is a stale `Alt-Ergo,2.6.2,` pin against an
installed 2.6.3, so bare runs silently go Z3-only and report FALSE "unproven":**
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <file> --import-path src/pycsl \
    --provers "Alt-Ergo,2.6.3,,Z3,4.13.3,"
```
1. Whole-file proof of `src/self-annotate/src/frontend/Module2_Parser.py` = 0 non-Valid.
2. **CORPUS BYTE-DIFF — the HARD gate.** This edits shared `src/pycsl` record construction. Build a
   worktree-at-HEAD baseline, symlink the repo `.venv` into it, run ONE foreground sweep per side,
   and **read the `emitted N` line on BOTH sides — assert N is EQUAL and NONZERO** (a sweep that
   emitted 0 files is a false green; that has happened here before). Target: diff == 0. If the diff
   is non-zero, M1 applies: the diff must be EXACTLY the intended correction AND every affected
   corpus program must re-prove — otherwise tighten the gate until it is 0.
3. **§10c importer sweep** — L3-tc EVERY mirror that imports the changed theory, not just the
   changed file (a prior increment passed its own file + the corpus and still broke
   `Module5_IREmitter` L3-tc, and had to be reverted).
4. **Fidelity** — `bin/check-self-annotate-sync.sh` must show EXACTLY 2 DIVERGED
   (`expressions.py::_handle_var_expr`, `stmt_control_flow.py::_handle_for_stmt`);
   `bin/self-annotate-mirror-check.sh` EXACTLY 3 drifted (`expr_ghost_collections`, `statements`,
   `stmt_control_flow`). Both exit 1 at HEAD — that is the accepted BASELINE, do not "fix" it.
5. **Ledger == 3** — `proof_axiom_allowlist.py` untouched.
6. **Non-vacuity** — the emitted `forexpand_clauses` must be the REAL accumulated sequence.
   `bin/check-emitted-vacuity.py` exit 0.
7. **Count** — `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l` = 673 -> 672.

## Follow-ons if this lands (do NOT attempt in the same increment)
`_parse_happy_region` / `_parse_happy_targets` / `_parse_happy` (`HappyProperty.except_set`),
`_parse_no_exception` (needs a `NoExceptionDecl` return route — no `IrNoExceptionDecl` exists),
`_parse_contract`, then the `_Harvester` trio once `@mutable_state` + the real frame are fixed.

# `union-local-typing-impl.md` — L12 spike: give a call-bound local its callee's union type

Gate P: spike-first, refutation exit, PAYOFF GATE, three-L-plane battery.

## Hypothesis (to be REFUTED or confirmed by measurement, not argued)
The `Optional[X]` wall may be NARROW rather than a value-model rewrite. The union types are ALREADY
synthesized — `Module5_IREmitter.py:3427` registers `variant_name = f"_union_{safe_scope}_{idx}"`
from a `Optional[T]` / union ANNOTATION, per the scope the annotation appears in. What is missing is
**local-type inference for a local bound to a union-returning CALL**:
`stmt_control_flow.py:1977 _maybe_inject_union_return` handles union RETURNS, but nothing gives
`t` a type in `t = self.peek()` when `peek() -> Optional[Token]` lives in another scope. The local
falls back to `int`.

**Measured first blocker (driver, this window), `_Parser.parse_implication` ported verbatim:**
```
src/self-annotate/src/proof2why3/parser.mlw", line 414, characters 9-31:
This expression has type PyCSL_Program._union_peek_0, but is expected to have type int
```

## STEP 0 — MAKE-OR-BREAK SPIKE
Make a local assigned from a call to a union-returning function carry the callee's synthesized union
type (cross-scope: the union is named for the CALLEE's scope, e.g. `_union_peek_0`, while the local
lives in the caller). Smallest probe: `proof2why3/parser.py::_Parser.parse_implication` (8 live LOC).

**SPIKE PASSES** iff `parse_implication` reaches a passing L3-tc with the local correctly typed.
**REFUTATION EXIT:** if cross-scope union naming/ownership makes this ill-formed (e.g. the union type
is not in scope at the caller, or two callees' unions collide), STOP, revert by exact path, report the
exact error. CERTIFIED-BOUNDARY is a fully successful outcome. Do NOT start a general union/value-model
rewrite — that is the over-build this exit exists to prevent.

## PAYOFF GATE (same discipline that correctly killed L10)
After the spike passes, measure how many `\trusted` stubs actually convert. Candidates:
`proof2why3/parser.py` cursor family (`parse_implication`, `parse_comparison`,
`parse_atom_application`, `parse_quant`, `parse_atom`, `parse_type_expr` — every one uses
`peek() -> Optional[Token]`), `Module2_Parser::_parse_happy_targets`, `audit_proof::audit_both`.
**If ZERO convert, REVERT EVERYTHING AND LAND NOTHING** and report each remaining first blocker.

Known co-blockers you may hit — REFUTE and move on, do not fight:
- `Return <record>` for early returns of a MUTABLE record: a Why3 TYPE REJECTION
  (`has mutable components`). NOTE: it does NOT apply to the `proof2why3` Term family — `type term`
  is already emitted fully immutable (`list term` / `list string`), so `Return_term term` is legal.
- Empty WhyML record literal `{ }` for field-less marker dataclasses.
- Opaque getter / set-comprehension typing (`sorted({...})` -> `(sorted_1 (set_comp 0))`).

## STEP 1 — full battery, only if >= 1 stub converts
**Provers — the repo default is BROKEN here** (stale `Alt-Ergo,2.6.2,` pin vs installed 2.6.3 =>
bare runs go Z3-only and report FALSE "unproven"):
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <file> --import-path src/pycsl --provers "Alt-Ergo,2.6.3,,Z3,4.13.3,"
```
1. Whole-file proof of every changed mirror file = 0 non-Valid.
2. **Corpus byte-diff — HARD gate** (`src/pycsl` touched, and local typing is shared): worktree-at-HEAD
   baseline, repo `.venv` symlinked, read `emitted N` on BOTH sides, assert equal and NONZERO (**812**),
   `diff -rq` exit 0. Non-zero => M1: exact-diff + every affected program re-proves, else tighten.
3. §10c importer sweep: L3-tc all 52 mirror files.
4. Fidelity (both exit 1 — ACCEPTED baseline): sync exactly 2 DIVERGED
   (`expressions.py::_handle_var_expr`, `stmt_control_flow.py::_handle_for_stmt`); mirror-check exactly
   3 drifted (`expr_ghost_collections`, `statements`, `stmt_control_flow`); your file must NOT appear.
5. Ledger == 3; no new axiom; no new *trusted* val.
6. Vacuity: `bin/check-emitted-vacuity.py --emit`, assert population **52**; HEAD baseline is **EXIT=1**
   (6 known gated + 2 input-blind + pre-existing `Module3_Weaver::pycslweaver___const_int`); gate is
   NO NEW finding. Without `--emit` it reuses existing `.mlw` — a population of ZERO and a FALSE EXIT=0.
7. Count: currently **671**.

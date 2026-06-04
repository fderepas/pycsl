# Plan: module-level constants in contracts

## Context

Corpus 0290/0291 fail because module-level constants used in **contracts** are rejected. 0290
defines `K_IHDR = 0 … K_IEND = 3` and writes `#@ ensures \result == 0 ==> kinds[0] == K_IHDR`;
0291 defines `BASE` and uses it in a loop invariant. These names work fine in function **bodies**
(`if kind == K_IHDR`), but `Module4._validate_contract` walks the contract's identifiers and
raises `Undefined variable 'K_IHDR'` (Module4_SemanticAnalyzer.py:216) because module-level
constants are never added to the contract scope (`current_scope` holds only params, locals,
loop/ghost vars — built at ~:493-533).

PyCSL already solves the analogous problem for **class-body constants** (`CAP = 64` referenced as
`self.CAP` resolves to the literal `(64)`): collect (Module5 `_collect_class_constants` ~:1254) →
exclude from contract validation → resolve to a literal in Module6 (`_handle_field_get_expr`
expressions.py ~:1163, via `_class_constants`). **This plan mirrors that collect→validate→resolve
template for module-level constants**, so a module constant is inlined as its literal everywhere
(body and spec agree, proofs discharge).

## Plan (mirror the class-constant template)

1. **Collect (Module5).** New `_collect_module_constants(module_node)` (mirror
   `_collect_class_constants`): scan the `ast.Module` top level for `NAME = <int literal>`
   assignments where `NAME` is **assigned exactly once** in the module and is not a `#@ shared`
   var. Store `program_ir["module_constants"] = {name: int}`. Call it from `visit_Module`
   (Module5 ~:40) alongside the namedtuple pre-pass.

2. **Validate (Module4).** In `visit_Module` collect the same single-assignment int-literal module
   names into `self._module_constants: Dict[str,int]`; in `_validate_contract` (~:203-218), accept
   a referenced name when it is in `self._module_constants` (treat like an in-scope read-only
   name) instead of raising. Minimal change — one membership check before the raise at :216.

3. **Resolve (Module6).** Add `_module_constants: Dict[str,int]` (parallel to `_class_constants`),
   loaded from `program_ir["module_constants"]` in `transpile()`/preamble. In
   `_handle_var_expr` (expressions.py ~:1133), **before** the opaque `val constant X : int`
   fallback (~:1150), if `name in self._module_constants` return its literal `f"({val})"`. This
   applies in BOTH spec and body, so `K_IHDR` becomes `0` consistently — replacing the current
   opaque `val constant K_IHDR` and letting `kinds[0] == K_IHDR` discharge.

## Q2 — Are module-level *mutable* variables allowed in contracts? (No — and why)

A module name bound **once** to an int literal is a constant and is inlined (above). A module
name that is **reassigned** anywhere is mutable global state, and is deliberately NOT made
referenceable in contracts:
- A contract is a per-function pre/post relation; a value that changes across calls (and is not a
  parameter, field, or ghost) has no well-defined meaning in the per-function **frame model** —
  referencing it would be unsound without ghost-tracking / a frame clause over globals (not
  modelled).
- This matches the existing design: `#@ shared` concurrency globals are mutable and are
  intentionally excluded from contract scope (Module4 ~:506-520); and the class analog inlines
  class **constants** while instance state must go through `self.field`.

So the plan **adds module constants only**; mutable module globals stay out of contracts, with a
one-paragraph rationale in the static-semantics doc. (If a real demand-driver appears, the sound
path is a `#@ ghost` mirror of the global, not direct reference — deferred.)

## Q3 — Similar fails worth investigating?

The persistent full-sweep failure set was triaged (read-only) into root-cause buckets:

- **Fixed by this plan (2):** **0290, 0291** — the only two "module-constant-in-contract" failures
  (`K_IHDR`, `BASE`). Both flip to PASS.
- **Unrelated — cross-module contract propagation (27):** **0056-0065, 0168-0187** all import a
  function from `multi_file_lib.*` and fail with the solver reporting `Unknown (sat)` on the
  caller's postcondition — the imported callee's contract is not propagated into the caller's
  WhyML, so SMT has nothing to reason with. This is the **largest cluster** and a genuine
  separate gap (cross-module `ensures` propagation) worth its own plan — NOT a scope issue.
- **Unrelated — type error (1):** **0199** uses a `dict`-typed param with `\length`/array
  indexing → Why3 type mismatch (`map` vs `array`). Likely either needs dict-length support or
  should be re-marked `# pycsl-expected: FAIL` (it exercises an unsupported shape, not a bug).

So this plan clears 2 of the 30 persistent failures; the bucket-D multi-file cluster (27) is the
high-value follow-up.

## Reference corpus

- **0290 / 0291** flip to passing. Check whether they now **prove** (they are `# pycsl-flags:
  --no-proof` today); if the literal resolution makes them discharge, drop `--no-proof`.
- **New 0506** — a focused module-constant driver that PROVES with content (a `requires`/`ensures`
  referencing a module `LIMIT = 8`), no `--no-proof`.
- **New 0507 (negative, `# pycsl-expected: FAIL`)** — a false contract over a module constant
  (e.g. `ensures \result == LIMIT + 1` where the body returns `LIMIT`), proving the constant is
  real content.
- **New 0508 (boundary)** — a contract referencing a **reassigned** module global must still be
  rejected (documents Q2; expect the `Undefined variable` / unsupported error).

## Verification

Per file: `PYTHONHASHSEED=0 .venv/bin/python src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0290.py`
(0290/0291/0506 PASS; 0507/0508 FAIL-as-expected). Full corpus sweep (`/tmp/proof_sweep.sh`
pattern, diff vs baseline) — confirm 0290/0291 leave the regression set and nothing new breaks
(the change is additive: a name that was an opaque `val constant` becomes a literal only when it
is a recognised single-assignment module int-constant). Docs: a "module constants" note in
`docs/pycsl-static-semantics-reference.md` (τ / scope) + the Q2 mutable-global rationale;
`bin/doc-coherency.py --check` green.

## Critical files

- `src/pycsl/Module5_IREmitter.py` — `_collect_module_constants` + `visit_Module` wiring
  (~:40), `program_ir["module_constants"]`; mirror `_collect_class_constants` (~:1254).
- `src/pycsl/Module4_SemanticAnalyzer.py` — `_module_constants` collection in `visit_Module`
  (~:370); accept module constants in `_validate_contract` (~:216).
- `src/pycsl/module6_whyml/expressions.py` — `_handle_var_expr` literal resolution before the
  `val constant` fallback (~:1133-1150); `_module_constants` dict (mirror `_class_constants`).
- `src/pycsl/module6_whyml/preamble.py` — load `program_ir["module_constants"]` into
  `_module_constants` (mirror the `_class_constants` load ~:570).
- `test-suite/corpus/pycsl-reference/0290.py`, `0291.py` (flip), `0506–0508.py` (new); static-
  semantics doc.

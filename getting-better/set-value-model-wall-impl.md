# set-value-model-wall-impl.md — implementation plan (spike-first; emission-refutation exit)

Synthesized from `set-value-model-wall.md` + `-response.md` (Gate R **CONFIRM**, one mandatory emission rule). The
MODELING is proven (fable `scratchpad/set-oracle.mlw`: `fset string` mem/dedup goals Valid, evil-twin non-vacuous,
ledger-neutral). The impl make-or-break is the EMISSION.

## Design (per the fable mandatory rule)
- A local `s: Set[str] = set()` → an executable `set.SetApp[string]` value (NOT logic-only `set.Fset`/`map.Map`,
  which fail "used in a non-ghost context" in a program `if`). Emit `use set.SetApp with type … string` + a
  decidable program string-equality `val eq (x y: string): bool ensures { result <-> x = y }` (a decidable
  primitive, NOT a project axiom — ledger stays 3).
- `set()` → `SetApp.empty`; `s.add(x)` → `s := SetApp.add x !s`; `x not in s` → `not (SetApp.mem x !s)` (a program
  bool GUARD in the `if`). The spec plane (if ever needed) reasons at `Fset` logic level.
- **CRITICAL RULE:** the recogniser emits the `if not mem` GUARD only — it must NOT put a set-NON-membership fact in
  the contract/an assert (`assert { not (Fset.mem "c" !s) }` times out). The fixed `requires True / ensures True /
  assigns <frame>` shape satisfies this (no non-membership ensures). Verify no such obligation is emitted.
- Gated on a corpus-absent `Set[str]`-local sentinel → the 767 corpus stays byte-identical.

## Gate S — EMISSION make-or-break SPIKE FIRST (refutation exit)
1. Re-prove the fable oracle (`why3 prove -P z3 scratchpad/set-oracle.mlw`) → reproduce Valid + ledger-neutral.
2. Emit the Set[str]-local recogniser (gated on a new `_uses_str_set` signal) + a MINIMAL fixture: a method with a
   `Set[str]` local, `.add(x)`, an `if x not in s:` guard, reading a result. `pycsl <fixture> --keep-mlw`. Does
   `= set()` lower to `SetApp.empty : set string` (NOT `ref 0`), `.add`→`SetApp.add`, `not in`→`not (SetApp.mem …)`
   (program bool, NOT `contains_check (str_hash_op …)`), and TYPECHECK (L3-tc ✓) + the fixture PROVE?
   - PASS → build the recogniser fully.
   - REFUTE (SetApp clone won't emit / the string-eq val forces something / the guard won't type / it can't gate
     byte-inertly) → REVERT ALL, record CERTIFIED-BOUNDARY (§ GATE-S OUTCOME) with the exact Why3/emit error.

## Build (only if Gate S PASSES) — fixture-witness pattern (commit infra + fixture, count unchanged)
(a) preamble/emit: the `set.SetApp[string]` clone + decidable string-eq `val`, gated `_uses_str_set`.
(b) recognisers: `= set()` local → `set string` ref (`_prescan_str_set_locals`); `.add(x)` → `s := SetApp.add x !s`;
    `x in s`/`x not in s` → `SetApp.mem`/`not SetApp.mem` (program bool). No non-membership obligation.
(c) reference fixture `test-suite/corpus/pycsl-reference/0923_str_set_local.<ext>` (git add -f, 0918/0921/0922
    convention): builds a `Set[str]` local, adds, membership-guards, proves faithfully (non-vacuous; evil-twin).
Gate: fixture proves; corpus byte-diff 0 (gated ⇒ inert); ledger 3 (SetApp stdlib, string-eq val is decidable-prim,
no project axiom — verify `_AXIOM_REGISTRY`/allowlist untouched); fidelity 52/52. Count UNCHANGED (infra + fixture
witness — the L4a precedent). NO stub conversion in THIS increment.

## Follow-on (next increment) — converge `_collect_class_fields`
Co-land the Set[str] recogniser + the const-reflection node (isinstance(x,(int,float)) tuple-of-types + int(x)) + the
5 body-faithful helper ports (_m5_get_list_elem_type/_m5_get_field_key_type/_m5_get_option_field_inner/
_is_dataclass_decorated/_cf6_is_cases_list_of_dict) + L4a pyval + R2 ast.walk → convert `_collect_class_fields`
(count 1013→1012). Each residual measured; do them as sub-increments, spike-gated.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ (whole-file proof OR --fun+wedge-note) ∧ byte-diff-0 (gated) ∧ ledger==3 (no project axiom; SetApp/Fset
are trusted-stdlib) ∧ count (unchanged for infra+fixture; strictly down for a conversion) ∧ non-vacuity (MUTATION
TEST; real SetApp.add/mem, NO str_hash_op/contains_check/int-hash facade; NO non-membership proof obligation).

## Honest costed scope
The Set[str] recogniser (a + b + fixture) is the shared infra increment. The `_collect_class_fields` conversion is
the follow-on (const-reflection + 5 helpers). Refutation exit at Gate S if the SetApp emission walls (the model is
proven; the tool's executable-set emission is the residual risk).

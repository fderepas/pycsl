# set-value-model-wall.md — the emitter-local `Set[str]` value model (next collector-cascade node)

**For review. State-of-the-art report on the highest-leverage remaining node in the value-model collector cascade:
an emitter method's LOCAL `Set[str]` value (`s = set(); s.add(x); x not in s`), which currently int-erases.**

## 1. Global picture
PyCSL lowers annotated Python to WhyML discharged by Why3/SMT. The self-annotation effort mirrors the live emitter
into `src/self-annotate/src/` and drives its `#@ \trusted` stub count DOWN under a fixed contract, gated by three
disjoint oracle planes (fidelity, whole-file Why3 proof, corpus byte-diff-0). Count is **1013**, ledger **3** (must
stay 3). Prior runs broke the heterogeneous `Dict[str,Any]` value-model wall + built a cascade of committed,
axiom-free, fixture-witnessed value-model ADTs (pyval / Call-internals / tparam reflection-node / self-field
seq-pyval append / the L4a pyval value-model recognizers), converting `_collect_typevar_registry`,
`_collect_final_registry`, `_collect_type_params`. The measured next floor: the 3 remaining Module5 collector stubs
each need a NEW node-value-model subsystem. THIS report is the highest-leverage one.

## 2. The wall — first seen
`_collect_class_fields` (live `frontend/Module5_IREmitter.py`) dedups field names with an emitter-method LOCAL set:
```python
field_names_seen: Set[str] = set()
...
if name not in field_names_seen:
    field_names_seen.add(name)
    fields.append({...})
```
The tool int-erases the local set: `= set()` → `ref 0`; `.add(x)` → opaque; `x not in s` → `contains_check
(str_hash_op x) 0` (int-hash membership facade). ZERO precedent: no converted mirror method constructs/uses a LOCAL
`set()` value (the existing `_csl_set_*` methods emit USER-code set exprs; `= set()` at line 2435 is inside a
`\trusted` stub). The verbatim-fidelity gate forbids dropping the dedup, so `_collect_class_fields` cannot convert
until an emitter-local `Set[str]` value is modelled faithfully.

## 3. The deeper truth — a modeling choice, NOT a fundamental limit
A Python `Set[str]` is a finite set of strings. Why3 has native finite-set theory (`set.Fset` / `set.Set`): a
local `s: Set[str]` is `Fset.fset string`; `s = set()` → `Fset.empty`; `s.add(x)` → `s := Fset.add x s`; `x in s`
→ `Fset.mem x s`; `x not in s` → `not (Fset.mem x s)`. All Why3-intrinsic — no int-hash, no new axiom. (Alternative:
a `map string bool` characteristic function.) This is the string-set analogue of the K1 seq-pyval field / the L4a
map-pyval read — a value-model recogniser over an EXISTING sound theory.

## 4. SOTA lens — the value-model recogniser over Why3 set theory
The precedent is direct: the campaign already models a local `seq pyval` (K1/L4a) + a `map string (option pyval)`
field faithfully. A local `Fset.fset string` is one step over — a finite-set value with `add`/`mem` ops. The NEW
capability is (a) typing a `= set()` local (annotated `Set[str]`) as `Fset.fset string`, (b) `.add`/`in`/`not in`
recognisers lowering to `Fset.add`/`Fset.mem`. Gated on a corpus-absent `Set[str]`-local sentinel → byte-inert.

## 5. Honestly-costed routes
- **R-set (make-or-break): a local `Fset.fset string` value model + `.add`/`in`/`not in` recognisers.** Fixture-
  witness pattern (the L4a precedent): commit the recogniser as infra + a reference fixture that builds a local set,
  adds, tests membership, proves — WITHOUT a stub conversion (count unchanged). Reuse Why3 `set.Fset` — likely NO
  new cert (Fset is Why3-intrinsic; if a shape needs one, an axiom-free `Phase2i_SetStr` side-car). Then converge
  `_collect_class_fields` with the OTHER two residuals (isinstance-tuple const-reflection + 5 body-faithful helper
  ports) in a follow-on increment.
- **R0 (fallback): `map string bool` characteristic function** if `Fset` has an emission/positivity snag.

## 6. Honest limits + certificate
The risk is EMISSION, not modeling (Why3 `set.Fset` is sound + intrinsic): (a) does the tool emit a `= set()` local
as `Fset.empty : fset string` (not `ref 0`) and `.add`/`in` as `Fset.add`/`Fset.mem` (not int-hash)? (b) does a
local-set method typecheck + prove non-vacuously? (c) ledger stays 3 (Fset needs no axiom). Each is a spike question.
`_collect_class_fields`'s FULL conversion additionally needs the const-reflection node + 5 helper ports (separate,
measured session-scale) — but R-set is the gating shared piece and commits standalone (fixture-witness).

## 7. The make-or-break question for review
Does an emitter-method LOCAL `Set[str]` modelled as `Fset.fset string` — `set()`→`Fset.empty`, `.add(x)`→`Fset.add
x s`, `x not in s`→`not (Fset.mem x s)` — **typecheck and PROVE non-vacuously** (a set built + added-to + membership-
tested reads back faithfully; an evil-twin membership claim fails), **axiom-free** (ledger 3)? Or does Why3 `Fset`
over `string` hit an emission/type snag forcing `map string bool` (R0) or an axiom? **An oracle run — a hand `.mlw`
with a `fset string` local, `Fset.add`/`Fset.mem`, a driver proving `mem x (add x empty)` ∧ `not (mem y (add x
empty))` for `x<>y`, `why3 prove -P z3`, + an axiom check — should CONFIRM or REFUTE before any emitter edit.**

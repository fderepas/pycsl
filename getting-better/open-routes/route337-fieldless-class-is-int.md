# OPEN ROUTE #337 — A USER CLASS WITH NO INSTANCE FIELDS IS LOWERED TO `type w = int` (user dunders ignored, int laws on its instances)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; opened the same day), Severity 1.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates each function — run the file to list them).
Witness `witnesses-r337/F2_fieldless_class_int.py` (3 functions): a user `__sub__` is ignored, `x - x == 0` proves; with `class P: pass`, `x < x` and
`x * 0 + 1` prove under no_exception \all (CPython TypeError). #249 only covers `==` on classes defining __eq__.
Repair: a fieldless user class must be an ABSTRACT type (no arithmetic/ordering), and operators on it must dispatch to the user dunder (or refuse).

## REPAIR (2026-10-24, r336b, repaired together with route #336 — see route336 REPAIR for commits, design, movers and gates)
A field-less user class is no longer a lowered type: its tag is outside Module 6's lowered set, so a parameter / return annotated
with it is the ERASED object of route #249 (no int law; arithmetic and ordering uninterpreted, refused under `no_exception` or into
a builtin-typed slot, route #252); `Optional[P]` erases the whole annotation (no opaque-int arm). User dunders are therefore never
contradicted (the model claims nothing about `x - x`), rather than dispatched.

| shape | ebd6f814 | after |
|---|---|---|
| `W.__sub__` returns 1, `x - x == 0` (4509) | PROVED | REFUSED (erased into `-> int`) |
| `class P: pass`, `x < x` under `no_exception` (4510) | PROVED | FAIL |
| `class P: pass`, `x * 0 + 1` under `no_exception` (4511) | PROVED | REFUSED |
| method of field-less `W`: `self - self == 0` with `__sub__` returning 1 (4524) | PROVED | REFUSED `PYCSL-R337-SELF-OPERATOR` |
| method of `class P`: `self < self` under `no_exception` (4527) | PROVED | REFUSED `PYCSL-R337-SELF-OPERATOR` |
| control `x is x` (4528), record class `p.x - p.y` (4529) | PROVED | PROVED |

The `self` receiver of a non-record class's methods is still `type <c> = int` (the mirror's emitter classes depend on it,
21 such aliases across the 53 mirrors), so arithmetic / ordering operators applied to `self` are REFUSED in Module 5
(`PYCSL-R337-SELF-OPERATOR`; census: zero such uses in corpus, pyref and mirror, so the rule is mover-free).

Mover: 3107 (fieldless MRO chain, `use(a: A)` now `-> object`, goal still reached and failing). Residuals: a method call on a
field-less instance returns an erased value (more refusals in builtin-typed slots, 1 corpus file); user dunders are not dispatched
to (sound by erasure / refusal, not modelled); `type w = int` is still emitted as the receiver type of its methods, guarded
only by the syntactic `self`-operator refusal (a local alias `s = self; s - s` is not followed).

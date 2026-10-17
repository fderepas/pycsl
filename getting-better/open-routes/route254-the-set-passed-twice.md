# OPEN ROUTE #254 — ONE dict/set PASSED TO A MUTATING SLOT AND A READ SLOT OF THE SAME CALL

**Status: REPAIRED (gen #36, 2026-10-17; opened 2026-10-16), Severity 1.** See "Repair" at the end. Found by the driver's red-team probe; driver-reproduced at
HEAD fa283db6 (both rc=0; CPython True).

## Witnesses (`witnesses-r254/`)
- `p21_set_param_double.py`: `g(x, y)` (`assigns x`) does `x.add(1)`, returns `1 in y` under
  `requires not (1 in y)`, `ensures \result == False`; caller `a = set(); return g(a, a)` proves `\result == False`.
- `p18_dict_param_double_req.py`: the dict version (`x[1] = 5`).

## Mechanism
The mutated parameter is a `ref`, the read-only one a value: `(g a !a)` — Why3's alias check compares refs only,
and the #243/#244 rule ("an argument in a mutating slot must be fresh or single-use") does not see `a` used twice
IN THE SAME CALL. The callee's contract is false whenever `x is y`. Lists are safe (Why3 "illegal alias").

## Repair direction
Extend the #243/#244 mutating-slot rule: an argument in a mutating slot must not also appear (or alias) in any
other argument of the same call; and/or treat the callee's read-only dict/set params as possibly aliasing its
mutated ones (havoc them after the mutation).

## Repair (gen #36, 2026-10-17)
Rule (fail-closed, inline in `functions.py::_reset_function_state`, the #243/#244 block, code
PYCSL-WHYML-COLLECTION-ALIAS, same raise site and message frame): for every call of the function being
emitted, the MUTATING slots are the #244 shadow slots (`_x_slots[...]["mut"]`) PLUS the WL-05b by-ref
slots (`_func_mutated_collection_params`, the `ref (map ...)` params — the population the #243/#244 rule
never saw). The argument `v` in such a slot must not be named aliasingly (the (M) rule's walk: stored /
bound / returned / passed on; not `len(v)` or `v.copy()`) by ANY OTHER argument of the call, positional or
keyword; and when another argument names anything (scalar-typed names excepted), `v` must be a name nothing
else can hold — a parameter not rebound (its callers are checked by this same rule: the slot is forwarded
by WL-05b's fixpoint) or a local bound only to fresh values, never given another name before, outside a
loop — and no other argument may be a local bound to a non-fresh value when `v` is a parameter.
Witnesses (PROVED at e6f26cde, REFUSED now; CPython ground truth in each `__main__`): 2540 set twice, 2541
dict twice, 2542 keyword (`g(a, y=a)`), 2543/2544 local alias `b = a` (set/dict), 2545 forwarded through
`mm(p, q)`, 2546 `del x[1]`. Control 2548 (distinct objects, forwarded distinct, fresh literal) PASS.
Blast radius: one root file GONE, 0884 (FAIL -> REFUSED: a recursive walker passes an element of an `Any`
container beside its mutated accumulator — the element may BE the accumulator). Mirror 0 MOVED.
Residual (model assumption, not this route): an ENTRY function's parameters passed from unverified code
may alias (Why3's own alias assumption for refs; cf. FIELD-DISJOINT, route #256).

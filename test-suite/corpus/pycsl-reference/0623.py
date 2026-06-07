"""Test 0623 — collection-typed quantifier binders (07-1311 Q4).

A binder may range over a whole collection: `\\forall a : list;` (WhyML `array int`) and
`\\forall m : dict;` (`map int (option int)`). `\\length(a)` and `m[k]` lower to `Array.length`
and `Map.get` respectively (the dict binder is registered so `m[k]` is a map lookup, not the
abstract int subscript). The needed theories are imported even with no array/map locals.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \forall a : list; \length(a) >= 0
#@ ensures \forall m : dict; \forall k : int; m[k] == m[k]
#@ assigns \nothing
def f() -> int:
    return 0

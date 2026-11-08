"""Test 1002 — NEGATIVE witness for the parametric `#@ datatype` (A5d) lowering.

The companion of `1003` and of `0540`. Same program, a postcondition that is
FALSE of it: `Just(7)` matched by `case Just(n)` binds `n == 7`, so `\result`
is 7 and never 8.

WHY THIS FILE EXISTS. Until relaunch #45 a parametric `#@ datatype Option[T]`
never reached Module 6 at all — `frontend/monomorphize._collect_generic_decls`
read the variant decl's `type_params` (a list of BARE NAMES, `["T"]`, written by
`Module5_IREmitter`) as the PEP 695 shape (`[{"name","bound","kind"}]`, the
ir_schema v1.4 shape written for `class C[T]:`), and `_check_gt3_schema_only`
died with `'str' object has no attribute 'get'`. Enabling the lowering must not
be allowed to enable a VACUOUS one: if the payload were erased to a constant or
the match arm lowered to a fabricated value, a false `\result` could become
provable. This file is the guard on that.
"""
# pycsl-expected: FAIL
#@ datatype Option[T] = Nothing | Just(T)
_ = 0  # anchor


#@ ensures \result == 8
#@ assigns \nothing
def use_int() -> int:
    o = Just(7)
    match o:
        case Just(n):
            return n
        case Nothing():
            return 0

"""Test 0633 — negative: isinstance against a wrong leaf type decides FALSE (07-1839 P4).

`isinstance(x, str)` for an `int`-typed `x` lowers to `subtag tag_int tag_str` = false (leaf≠leaf),
so asserting it as a postcondition cannot be proven — isinstance never spuriously certifies a wrong
type (the anti-unsoundness direction).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures isinstance(x, str)
#@ assigns \nothing
def f(x: int) -> int:
    return x

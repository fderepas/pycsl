"""Test 0632 — isinstance decided via metatype tags + \subtag (07-1839 P4).

`isinstance(x, T)` lowers to `subtag (\typeof x) T` over an int-tag enum (decision A: bool→int,
no tag_bool). A value's tag comes from Γ's τ; `\subtag` is reflexive + `<: object`. So
`isinstance(x:int, int)` and `isinstance(x, object)` (base type) and `isinstance(s:str, str)` all
DECIDE true and prove — not an opaque `isinstance_check`.
"""
# pycsl-flags: --memory-model hoare


#@ requires isinstance(x, int)
#@ ensures isinstance(x, object)
#@ assigns \nothing
def f(x: int) -> int:
    return x


#@ ensures isinstance(s, str)
#@ assigns \nothing
def g(s: str) -> int:
    return 0

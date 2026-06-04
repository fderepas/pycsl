"""Test 0474 — strings: __contains__ (`needle in haystack`).

Substring containment as a bool. PROVES as of strings-plan Stage 2: `in` over string
operands lowers to an uninterpreted `val str_contains_op (haystack needle : string) : bool`
(if-form for the bool return, as in 0475). The *content witness* — relating True to the
existence of a matching position — is the hard existential SMT goal and is deferred (the op
is uninterpreted here); a later stage can strengthen its `ensures`."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(needle) <= \str_length(haystack)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def contains(haystack: str, needle: str) -> int:
    if needle in haystack:
        return 1
    return 0

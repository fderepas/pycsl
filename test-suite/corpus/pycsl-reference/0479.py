"""Test 0479 — strings: __gt__ (`s > t`, lexicographic).
Target: lexicographic comparison. PROVES as of the G2 strings feature: `>` reflects to
`str_lt_op t s` (`s > t` ⇔ `t < s`), tied by `ensures` to the Why3 lexicographic predicate
`String.lt`; the body returns Python's int truth value (`if … then 1 else 0`)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def gt(s: str, t: str) -> bool:
    return s > t

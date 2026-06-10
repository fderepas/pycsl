"""Test 0480 — strings: __ge__ (`s >= t`, lexicographic).
Target: lexicographic comparison. PROVES as of the G2 strings feature: `>=` reflects to
`str_le_op t s` (`s >= t` ⇔ `t <= s`), tied by `ensures` to the Why3 lexicographic predicate
`String.le`; the body returns Python's int truth value (`if … then 1 else 0`)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def ge(s: str, t: str) -> bool:
    return s >= t

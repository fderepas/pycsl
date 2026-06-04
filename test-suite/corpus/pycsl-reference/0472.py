"""Test 0472 — strings: __len__ (`len(s)`).
`len` on a runtime `str` returns its Why3 `String.length`. PROVES as of strings-plan
Stage 1: `str` params are typed Why3 `string`; the spec `\str_length` uses the logic
`String.length`, and the body `len(s)` bridges to it via an abstract `str_length_op` whose
`ensures` ties the program result to `String.length` (the logic symbol cannot be used in a
program context directly)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \result == \str_length(s)
#@ assigns \nothing
def slen(s: str) -> int:
    return len(s)
